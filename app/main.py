from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import datetime
import json
from jose import JWTError, jwt
from passlib.context import CryptContext

from . import models, schemas, security
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee-Client Matching System")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройки JWT
SECRET_KEY = "your-secret-key"  # В продакшене использовать безопасный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_first_superuser(db: Session) -> bool:
    return db.query(models.Employee).filter(models.Employee.is_superuser == True).first() is None

@app.post("/first-superuser/", response_model=schemas.Employee)
def create_first_superuser(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    if not get_first_superuser(db):
        raise HTTPException(
            status_code=400,
            detail="Superuser already exists"
        )
    
    db_employee = security.get_employee(db, name=employee.name)
    if db_employee:
        raise HTTPException(status_code=400, detail="Name already registered")
    
    hashed_password = security.get_password_hash(employee.password)
    db_employee = models.Employee(
        **employee.dict(exclude={"password"}),
        hashed_password=hashed_password,
        is_superuser=True
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    employee = security.authenticate_employee(db, form_data.username, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": employee.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/employees/", response_model=schemas.Employee)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """
    Создание нового сотрудника. Доступно только суперпользователям.
    """
    db_employee = security.get_employee(db, name=employee.name)
    if db_employee:
        raise HTTPException(status_code=400, detail="Name already registered")
    hashed_password = security.get_password_hash(employee.password)
    db_employee = models.Employee(
        **employee.dict(exclude={"password"}),
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False  # Обычный пользователь
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    return employees

@app.post("/clients/", response_model=schemas.Client)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients/", response_model=List[schemas.Client])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    clients = db.query(models.Client).offset(skip).limit(limit).all()
    return clients

@app.post("/communications/", response_model=schemas.Communication)
def create_communication(
    communication: schemas.CommunicationCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    employee = db.query(models.Employee).filter(models.Employee.id == communication.employee_id).first()
    if not employee or not employee.is_active or employee.group == "significantly_below":
        raise HTTPException(status_code=400, detail="Employee not available for communication")
    
    db_communication = models.Communication(
        **communication.dict(),
        timestamp=datetime.datetime.now().isoformat()
    )
    db.add(db_communication)
    db.commit()
    db.refresh(db_communication)
    return db_communication

@app.get("/communications/", response_model=List[schemas.Communication])
def read_communications(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    query = db.query(models.Communication)
    if client_id:
        query = query.filter(models.Communication.client_id == client_id)
    if employee_id:
        query = query.filter(models.Communication.employee_id == employee_id)
    communications = query.offset(skip).limit(limit).all()
    return communications

@app.put("/employees/{employee_id}/group", response_model=schemas.Employee)
def update_employee_group(
    employee_id: int,
    group: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """
    Изменение группы сотрудника.
    Доступно только суперпользователям.
    """
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Проверяем валидность группы
    valid_groups = ["normal", "slightly_below", "significantly_below"]
    if group not in valid_groups:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid group. Must be one of: {', '.join(valid_groups)}"
        )

    # Обновляем группу
    employee.group = group
    db.commit()
    db.refresh(employee)
    return employee

@app.get("/match/{client_id}", response_model=schemas.Employee)
def match_client_to_employee(
    client_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Подбор сотрудника для клиента.
    Сотрудники с группой "significantly_below" не участвуют в маршрутизации.
    """
    # Проверяем существование клиента
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Получаем историю коммуникаций клиента
    client_communications = db.query(models.Communication).filter(
        models.Communication.client_id == client_id
    ).all()
    
    # Находим сотрудников, которые успешно общались с клиентом
    successful_employees = set()
    for comm in client_communications:
        if comm.success_rate > 0.7:
            successful_employees.add(comm.employee_id)
    
    # Ищем доступного сотрудника
    available_employee = db.query(models.Employee).filter(
        models.Employee.is_active == True,
        models.Employee.group != "significantly_below",  # Исключаем сотрудников с низкой стрессоустойчивостью
        models.Employee.id.in_(successful_employees) if successful_employees else True
    ).order_by(models.Employee.stress_level.asc()).first()
    
    if not available_employee:
        raise HTTPException(status_code=404, detail="No suitable employee found")
    
    return available_employee

@app.post("/tests/audio/{employee_id}", response_model=schemas.TestResult)
async def process_audio_test(
    employee_id: int,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Обработка аудио-теста для сотрудника.
    В будущем здесь будет интеграция с ML-моделью.
    """
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # TODO: Здесь будет обработка аудио с помощью ML
    # Пока что возвращаем заглушку
    test_result = models.TestResult(
        employee_id=employee_id,
        test_type="audio",
        score=0.75,  # Заглушка
        details={
            "file_name": audio_file.filename,
            "file_size": audio_file.size,
            "analysis": "Placeholder for ML analysis"
        }
    )
    
    db.add(test_result)
    db.commit()
    db.refresh(test_result)
    return test_result

@app.post("/tests/video/{employee_id}", response_model=schemas.TestResult)
async def process_video_test(
    employee_id: int,
    video_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Обработка видео-теста для сотрудника.
    В будущем здесь будет интеграция с ML-моделью.
    """
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # TODO: Здесь будет обработка видео с помощью ML
    # Пока что возвращаем заглушку
    test_result = models.TestResult(
        employee_id=employee_id,
        test_type="video",
        score=0.8,  # Заглушка
        details={
            "file_name": video_file.filename,
            "file_size": video_file.size,
            "analysis": "Placeholder for ML analysis"
        }
    )
    
    db.add(test_result)
    db.commit()
    db.refresh(test_result)
    return test_result

def update_employee_group_based_on_tests(employee_id: int, db: Session):
    """
    Обновление группы сотрудника на основе результатов тестов.
    """
    # Получаем последние результаты тестов
    test_results = db.query(models.TestResult).filter(
        models.TestResult.employee_id == employee_id
    ).order_by(models.TestResult.timestamp.desc()).all()

    if not test_results:
        return

    # Получаем сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        return

    # Анализируем результаты тестов
    total_score = 0
    test_count = 0

    for result in test_results:
        if result.test_type in ["multiple_choice", "questionnaire"]:
            total_score += result.score
            test_count += 1

    if test_count == 0:
        return

    average_score = total_score / test_count

    # Определяем группу на основе среднего балла
    if average_score >= 0.7:
        new_group = "normal"
    elif average_score >= 0.5:
        new_group = "slightly_below"
    else:
        new_group = "significantly_below"

    # Обновляем группу, если она изменилась
    if employee.group != new_group:
        employee.group = new_group
        db.commit()
        db.refresh(employee)

@app.post("/tests/questionnaire/{employee_id}", response_model=schemas.TestResult)
async def process_questionnaire(
    employee_id: int,
    questionnaire: schemas.QuestionnaireRequest,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Обработка анкеты для сотрудника.
    """
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Простая логика подсчета баллов (заглушка)
    total_questions = len(questionnaire.answers)
    correct_answers = sum(1 for answer in questionnaire.answers.values() if answer)
    score = correct_answers / total_questions if total_questions > 0 else 0

    test_result = models.TestResult(
        employee_id=employee_id,
        test_type="questionnaire",
        score=score,
        details={
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "answers": questionnaire.answers
        }
    )
    
    db.add(test_result)
    db.commit()
    db.refresh(test_result)

    # Обновляем группу сотрудника на основе результатов тестов
    update_employee_group_based_on_tests(employee_id, db)

    return test_result

@app.get("/tests/latest/{employee_id}", response_model=schemas.TestResult)
async def get_latest_test_result(
    employee_id: int,
    test_type: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Получение последнего результата теста определенного типа.
    """
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Получаем последний результат теста
    test_result = db.query(models.TestResult).filter(
        models.TestResult.employee_id == employee_id,
        models.TestResult.test_type == test_type
    ).order_by(models.TestResult.timestamp.desc()).first()
    
    if not test_result:
        raise HTTPException(
            status_code=404,
            detail=f"No {test_type} test results found for employee {employee_id}. Please complete the test first."
        )
    
    return test_result

@app.get("/tests/results/{employee_id}", response_model=List[schemas.TestResult])
async def get_test_results(
    employee_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Получение результатов всех тестов сотрудника.
    """
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Получаем все результаты тестов
    test_results = db.query(models.TestResult).filter(
        models.TestResult.employee_id == employee_id
    ).order_by(models.TestResult.timestamp.desc()).all()
    
    if not test_results:
        raise HTTPException(
            status_code=404,
            detail=f"No test results found for employee {employee_id}. Please complete some tests first."
        )
    
    return test_results

@app.post("/tests/multiple-choice/", response_model=schemas.MultipleChoiceTest)
def create_multiple_choice_test(
    test: schemas.MultipleChoiceTestCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """
    Создание нового теста с вариантами ответов.
    Доступно только суперпользователям.
    """
    # Проверяем формат вопросов
    questions_with_ids = []
    for i, question in enumerate(test.questions):
        if len(question.options) != 4:
            raise HTTPException(
                status_code=400,
                detail="Each question must have exactly 4 options"
            )
        if not 0 <= question.correct_option < 4:
            raise HTTPException(
                status_code=400,
                detail="Correct option index must be between 0 and 3"
            )
        # Добавляем ID к вопросу
        question_dict = question.dict()
        question_dict["id"] = i + 1
        questions_with_ids.append(question_dict)

    # Создаем тест
    db_test = models.MultipleChoiceTest(
        title=test.title,
        description=test.description,
        questions=questions_with_ids,
        is_active=True
    )
    
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@app.get("/tests/multiple-choice/", response_model=List[schemas.MultipleChoiceTest])
def list_multiple_choice_tests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Получение списка доступных тестов с вариантами ответов.
    """
    tests = db.query(models.MultipleChoiceTest).filter(
        models.MultipleChoiceTest.is_active == True
    ).offset(skip).limit(limit).all()
    return tests

@app.post("/tests/multiple-choice/{test_id}/submit", response_model=schemas.TestResult)
def submit_multiple_choice_test(
    test_id: int,
    submission: schemas.TestSubmission,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """
    Отправка ответов на тест с вариантами ответов.
    """
    # Получаем тест
    test = db.query(models.MultipleChoiceTest).filter(
        models.MultipleChoiceTest.id == test_id,
        models.MultipleChoiceTest.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Проверяем, что все вопросы теста отвечены
    if len(submission.answers) != len(test.questions):
        raise HTTPException(
            status_code=400,
            detail="All questions must be answered"
        )

    # Подсчитываем правильные ответы
    correct_answers = 0
    total_questions = len(test.questions)
    
    for answer in submission.answers:
        # Проверяем, что индекс вопроса в пределах
        if not 0 <= answer.question_id - 1 < len(test.questions):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid question ID: {answer.question_id}"
            )
        
        question = test.questions[answer.question_id - 1]
        if answer.selected_option == question["correct_option"]:
            correct_answers += 1

    # Создаем результат теста
    score = correct_answers / total_questions if total_questions > 0 else 0
    
    test_result = models.TestResult(
        employee_id=current_employee.id,
        test_type="multiple_choice",
        score=score,
        details={
            "test_id": test_id,
            "test_title": test.title,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "answers": [a.dict() for a in submission.answers]
        }
    )
    
    db.add(test_result)
    db.commit()
    db.refresh(test_result)

    # Обновляем группу сотрудника на основе результатов тестов
    update_employee_group_based_on_tests(current_employee.id, db)

    return test_result

@app.get("/employees/me/", response_model=schemas.Employee)
async def read_employees_me(current_employee: models.Employee = Depends(security.get_current_employee)):
    return current_employee

@app.post("/test-results/", response_model=schemas.TestResult)
def create_test_result(
    test_result: schemas.TestResultCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    db_test_result = models.TestResult(**test_result.dict())
    db.add(db_test_result)
    db.commit()
    db.refresh(db_test_result)
    return db_test_result

@app.get("/test-results/", response_model=List[schemas.TestResult])
def read_test_results(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    test_results = db.query(models.TestResult).offset(skip).limit(limit).all()
    return test_results

@app.post("/multiple-choice-tests/", response_model=schemas.MultipleChoiceTest)
def create_multiple_choice_test(
    test: schemas.MultipleChoiceTestCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    db_test = models.MultipleChoiceTest(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@app.get("/multiple-choice-tests/", response_model=List[schemas.MultipleChoiceTest])
def read_multiple_choice_tests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    tests = db.query(models.MultipleChoiceTest).offset(skip).limit(limit).all()
    return tests

@app.put("/communications/{communication_id}", response_model=schemas.Communication)
def update_communication(
    communication_id: int,
    communication_update: schemas.CommunicationUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    db_communication = db.query(models.Communication).filter(models.Communication.id == communication_id).first()
    if not db_communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    
    for field, value in communication_update.dict(exclude_unset=True).items():
        setattr(db_communication, field, value)
    
    db.commit()
    db.refresh(db_communication)
    return db_communication

@app.get("/clients/{client_id}/preferred-employees", response_model=List[schemas.Employee])
def get_client_preferred_employees(
    client_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    preferred_employees = db.query(models.Employee).filter(
        models.Employee.id.in_(client.preferred_employees)
    ).all()
    return preferred_employees

@app.post("/clients/{client_id}/preferred-employees/{employee_id}")
def add_preferred_employee(
    client_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if employee_id not in client.preferred_employees:
        client.preferred_employees.append(employee_id)
        db.commit()
    
    return {"message": "Employee added to preferred list"}

@app.delete("/clients/{client_id}/preferred-employees/{employee_id}")
def remove_preferred_employee(
    client_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if employee_id in client.preferred_employees:
        client.preferred_employees.remove(employee_id)
        db.commit()
    
    return {"message": "Employee removed from preferred list"} 