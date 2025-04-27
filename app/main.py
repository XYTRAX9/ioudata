import logging
import uvicorn
import asyncio
import json
import datetime
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, APIRouter, WebSocket, WebSocketDisconnect, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict, Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from . import models, schemas, security, chat
from .database import SessionLocal, engine, Base
from .init_db import init_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


app = FastAPI(title="Employee-Client Matching System", redirect_slashes=False)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка статических файлов
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройки JWT
SECRET_KEY = "your-secret-key"  # В продакшене использовать безопасный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_first_superuser(db: Session) -> bool:
    return db.query(models.Employee).filter(models.Employee.is_superuser == True).first() is None

# Роутеры
auth_router = APIRouter(prefix="/auth", tags=["Аутентификация"])
employees_router = APIRouter(prefix="/employees", tags=["Сотрудники"])
clients_router = APIRouter(prefix="/clients", tags=["Клиенты"])
communications_router = APIRouter(prefix="/communications", tags=["Коммуникации"])
tests_router = APIRouter(prefix="/tests", tags=["Тесты"])
profile_router = APIRouter(prefix="/profile", tags=["Профиль"])
admin_router = APIRouter(prefix="/admin", tags=["Администрирование"])

# Аутентификация
@auth_router.post("/first-superuser/", response_model=schemas.Employee)
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
        **employee.model_dump(exclude={"password", "is_active", "is_superuser"}),
        hashed_password=hashed_password,
        is_superuser=True
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@auth_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Получение токена доступа для сотрудника или клиента."""
    employee = security.authenticate_employee(db, form_data.username, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": employee.name, "type": "employee"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/client/register", response_model=schemas.Client)
async def register_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового клиента"""
    # Проверяем, не существует ли уже клиент с таким email
    db_client = db.query(models.Client).filter(models.Client.email == client.email).first()
    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Создаем нового клиента
    hashed_password = security.get_password_hash(client.password)
    db_client = models.Client(
        **client.model_dump(exclude={"password"}),
        hashed_password=hashed_password
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# Сотрудники
@employees_router.post("/", response_model=schemas.Employee)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Создание нового сотрудника. Доступно только суперпользователям."""
    db_employee = security.get_employee(db, name=employee.name)
    if db_employee:
        raise HTTPException(status_code=400, detail="Name already registered")
    hashed_password = security.get_password_hash(employee.password)
    db_employee = models.Employee(
        **employee.model_dump(exclude={"password", "is_superuser"}),
        hashed_password=hashed_password,
        is_superuser=False
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@employees_router.get("/", response_model=List[schemas.Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Получение списка всех сотрудников"""
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    return employees

@employees_router.get("/me", response_model=schemas.Employee)
async def read_employee_me(
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    """Получение информации о текущем сотруднике"""
    return current_employee

@employees_router.put("/{employee_id}/group", response_model=schemas.Employee)
def update_employee_group(
    employee_id: int,
    group: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Изменение группы сотрудника. Доступно только суперпользователям."""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    valid_groups = ["normal", "slightly_below", "significantly_below"]
    if group not in valid_groups:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid group. Must be one of: {', '.join(valid_groups)}"
        )

    # Обновляем группу
    employee.group = group
    
    # Обновляем уровень стресса в соответствии с группой
    if group == "normal":
        employee.stress_level = 1  # Норма
    elif group == "slightly_below":
        employee.stress_level = 2  # Чуть ниже нормы
    elif group == "significantly_below":
        employee.stress_level = 3  # Значительно ниже нормы
        
    logger.info(f"Обновлены группа и уровень стресса для сотрудника {employee.id}: группа={group}, стресс={employee.stress_level}")
    
    db.commit()
    db.refresh(employee)
    return employee

@employees_router.put("/{employee_id}/stress-level", response_model=schemas.Employee)
def update_employee_stress_level(
    employee_id: int,
    stress_level: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Обновление стрессового уровня сотрудника"""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not 1 <= stress_level <= 5:
        raise HTTPException(status_code=400, detail="Stress level must be between 1 and 5")
    
    employee.stress_level = stress_level
    db.commit()
    db.refresh(employee)
    return employee

@employees_router.get("/available", response_model=List[schemas.Employee])
def get_available_employees(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Получение списка доступных сотрудников с низким уровнем стресса"""
    employees = db.query(models.Employee).filter(
        models.Employee.is_active == True,
        models.Employee.stress_level.in_([1, 2])
    ).order_by(models.Employee.stress_level.asc()).all()
    return employees

# Клиенты
@clients_router.post("/", response_model=schemas.Client)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Создание нового клиента"""
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@clients_router.get("/", response_model=List[schemas.Client])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Получение списка всех клиентов"""
    clients = db.query(models.Client).offset(skip).limit(limit).all()
    return clients

@clients_router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Удаление клиента. Доступно только суперпользователям."""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    return None

@clients_router.get("/me", response_model=schemas.Client)
async def get_current_client(
    current_client: models.Client = Depends(security.get_current_client)
):
    """Получение информации о текущем клиенте"""
    return current_client

@clients_router.get("/{client_id}/match", response_model=schemas.Employee)
async def match_client_to_employee(
    client_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    """Подбор сотрудника для клиента"""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Получаем историю коммуникаций клиента
    client_communications = db.query(models.Communication).filter(
        models.Communication.client_id == client_id
    ).all()
    
    # Находим успешные коммуникации
    successful_employees = set()
    for comm in client_communications:
        if comm.success_rate > 0.7:
            successful_employees.add(comm.employee_id)
    
    # Исключаем сотрудников из черного списка
    available_employees = db.query(models.Employee).filter(
        models.Employee.is_active == True,
        models.Employee.group != "significantly_below",
        ~models.Employee.id.in_(client.blacklisted_employees)
    )
    
    # Если есть успешные сотрудники, выбираем из них
    if successful_employees:
        available_employees = available_employees.filter(
            models.Employee.id.in_(successful_employees)
        )
    
    # Выбираем сотрудника с наименьшим уровнем стресса
    employee = available_employees.order_by(models.Employee.stress_level.asc()).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="No suitable employee found")
    
    return employee

# Коммуникации
@communications_router.post("/", response_model=schemas.Communication)
def create_communication(
    communication: schemas.CommunicationCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Создание новой коммуникации"""
    print(f"Creating communication with data: {communication.model_dump()}")
    
    # Проверяем существование сотрудника
    employee = db.query(models.Employee).filter(models.Employee.id == communication.employee_id).first()
    print(f"Found employee: {employee}")
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if not employee.is_active:
        raise HTTPException(status_code=400, detail="Employee is not active")
    if employee.group == "significantly_below":
        raise HTTPException(status_code=400, detail="Employee is in significantly_below group")
    
    # Проверяем существование клиента
    client = db.query(models.Client).filter(models.Client.id == communication.client_id).first()
    print(f"Found client: {client}")
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        db_communication = models.Communication(
            **communication.model_dump(),
            timestamp=datetime.datetime.now()
        )
        print(f"Created communication object: {db_communication}")
        
        db.add(db_communication)
        db.commit()
        db.refresh(db_communication)
        print(f"Saved communication with ID: {db_communication.id}")
        
        return db_communication
    except Exception as e:
        print(f"Error creating communication: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@communications_router.get("/", response_model=List[schemas.Communication])
def read_communications(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Получение списка коммуникаций с возможностью фильтрации"""
    query = db.query(models.Communication)
    if client_id:
        query = query.filter(models.Communication.client_id == client_id)
    if employee_id:
        query = query.filter(models.Communication.employee_id == employee_id)
    communications = query.offset(skip).limit(limit).all()
    return communications

@communications_router.put("/{communication_id}", response_model=schemas.Communication)
def update_communication(
    communication_id: int,
    communication_update: schemas.CommunicationUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    """Обновление информации о коммуникации"""
    db_communication = db.query(models.Communication).filter(models.Communication.id == communication_id).first()
    if not db_communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    
    for field, value in communication_update.model_dump(exclude_unset=True).items():
        setattr(db_communication, field, value)
    
    db.commit()
    db.refresh(db_communication)
    return db_communication

@communications_router.put("/{communication_id}/feedback", response_model=schemas.Communication)
def update_communication_feedback(
    communication_id: int,
    feedback: schemas.CommunicationFeedback,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    """Обновление отзыва о коммуникации"""
    db_communication = db.query(models.Communication).filter(models.Communication.id == communication_id).first()
    if not db_communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    
    # Проверяем, что сотрудник имеет доступ к этой коммуникации
    if db_communication.employee_id != current_employee.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this communication")
    
    # Обновляем отзыв
    db_communication.employee_feedback = feedback.model_dump()
    
    # Обновляем успешность коммуникации
    if feedback.rating is not None:
        db_communication.success_rate = feedback.rating / 5.0
    
    # Обновляем стрессовый уровень сотрудника
    if feedback.stress_level is not None:
        current_employee.stress_level = feedback.stress_level
    
    db.commit()
    db.refresh(db_communication)
    return db_communication

@communications_router.post("/chat", response_model=schemas.Communication)
async def create_chat_communication(
    communication: schemas.CommunicationCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_employee)
):
    """Создание новой записи о чате"""
    db_communication = models.Communication(
        **communication.model_dump(),
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_communication)
    db.commit()
    db.refresh(db_communication)
    return db_communication

# Тесты
@tests_router.post("/multiple-choice/", response_model=schemas.MultipleChoiceTest)
def create_multiple_choice_test(
    test: schemas.MultipleChoiceTestCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Создание нового теста с вариантами ответов"""
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
        question_dict = question.model_dump()
        question_dict["id"] = i + 1
        questions_with_ids.append(question_dict)

    db_test = models.MultipleChoiceTest(
        title=test.title,
        description=test.description,
        questions=questions_with_ids
    )
    
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@tests_router.get("/multiple-choice/", response_model=List[schemas.MultipleChoiceTest])
def list_multiple_choice_tests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Получение списка доступных тестов"""
    tests = db.query(models.MultipleChoiceTest).filter(
        models.MultipleChoiceTest.is_active == True
    ).offset(skip).limit(limit).all()
    return tests

@tests_router.put("/multiple-choice/{test_id}/toggle-status", response_model=schemas.MultipleChoiceTest)
def toggle_test_status(
    test_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Изменение статуса активности теста. Доступно только суперпользователям."""
    test = db.query(models.MultipleChoiceTest).filter(models.MultipleChoiceTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test.is_active = not test.is_active
    db.commit()
    db.refresh(test)
    return test

@tests_router.delete("/multiple-choice/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Удаление теста. Доступно только суперпользователям."""
    test = db.query(models.MultipleChoiceTest).filter(models.MultipleChoiceTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    db.delete(test)
    db.commit()
    return None

@tests_router.post("/multiple-choice/{test_id}/submit", response_model=schemas.TestResult)
def submit_multiple_choice_test(
    test_id: int,
    submission: schemas.TestSubmission,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Отправка ответов на тест"""
    test = db.query(models.MultipleChoiceTest).filter(
        models.MultipleChoiceTest.id == test_id,
        models.MultipleChoiceTest.is_active == True
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    if len(submission.answers) != len(test.questions):
        raise HTTPException(
            status_code=400,
            detail="All questions must be answered"
        )

    correct_answers = 0
    total_questions = len(test.questions)
    
    for answer in submission.answers:
        if not 0 <= answer.question_id - 1 < len(test.questions):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid question ID: {answer.question_id}"
            )
        
        question = test.questions[answer.question_id - 1]
        if answer.selected_option == question["correct_option"]:
            correct_answers += 1

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
            "answers": [a.model_dump() for a in submission.answers]
        }
    )
    
    db.add(test_result)
    db.commit()
    db.refresh(test_result)

    update_employee_group_based_on_tests(current_employee.id, db)

    return test_result

# Профиль
@profile_router.get("/", response_model=schemas.EmployeeProfile)
async def get_employee_profile(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_active_employee)
):
    """Получение профиля сотрудника с историей коммуникаций и результатами тестов"""
    communications = db.query(models.Communication).filter(
        models.Communication.employee_id == current_employee.id
    ).all()
    
    test_results = db.query(models.TestResult).filter(
        models.TestResult.employee_id == current_employee.id
    ).all()
    
    profile = {
        "id": current_employee.id,
        "name": current_employee.name,
        "group": current_employee.group,
        "stress_level": current_employee.stress_level,
        "communications": communications,
        "test_results": test_results
    }
    
    return profile

# Эндпоинты для админской статистики
@admin_router.get("/stats/employees", tags=["Администрирование"])
async def get_employees_stats(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Получение статистики по сотрудникам для администратора."""
    total_employees = db.query(models.Employee).count()
    active_employees = db.query(models.Employee).filter(models.Employee.is_active == True).count()
    superusers = db.query(models.Employee).filter(models.Employee.is_superuser == True).count()
    
    by_group = {
        "normal": db.query(models.Employee).filter(models.Employee.group == "normal").count(),
        "slightly_below": db.query(models.Employee).filter(models.Employee.group == "slightly_below").count(),
        "significantly_below": db.query(models.Employee).filter(models.Employee.group == "significantly_below").count()
    }
    
    by_stress = {
        "low (1-3)": db.query(models.Employee).filter(models.Employee.stress_level <= 3).count(),
        "medium (4-7)": db.query(models.Employee).filter(models.Employee.stress_level > 3, models.Employee.stress_level <= 7).count(),
        "high (8-10)": db.query(models.Employee).filter(models.Employee.stress_level > 7).count()
    }
    
    return {
        "total": total_employees,
        "active": active_employees,
        "inactive": total_employees - active_employees,
        "superusers": superusers,
        "by_group": by_group,
        "by_stress": by_stress
    }

@admin_router.get("/stats/clients", tags=["Администрирование"])
async def get_clients_stats(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Получение статистики по клиентам для администратора."""
    total_clients = db.query(models.Client).count()
    
    # Количество клиентов с предпочтениями
    with_preferences = db.query(models.Client).filter(models.Client.preferred_employees != None, models.Client.preferred_employees != "[]").count()
    
    # Количество клиентов с черным списком
    with_blacklist = db.query(models.Client).filter(models.Client.blacklisted_employees != None, models.Client.blacklisted_employees != "[]").count()
    
    return {
        "total": total_clients,
        "with_preferences": with_preferences,
        "with_blacklist": with_blacklist
    }

@admin_router.get("/stats/communications", tags=["Администрирование"])
async def get_communications_stats(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Получение статистики по коммуникациям для администратора."""
    total_communications = db.query(models.Communication).count()
    
    # Статистика по типам звонков
    by_type = {}
    types = db.query(models.Communication.call_type).distinct().all()
    for type_tuple in types:
        call_type = type_tuple[0]
        count = db.query(models.Communication).filter(models.Communication.call_type == call_type).count()
        by_type[call_type] = count
    
    # Статистика по статусам
    by_status = {}
    statuses = db.query(models.Communication.status).distinct().all()
    for status_tuple in statuses:
        status = status_tuple[0]
        count = db.query(models.Communication).filter(models.Communication.status == status).count()
        by_status[status] = count
    
    # Средний рейтинг успешности
    avg_success = db.query(func.avg(models.Communication.success_rate)).scalar()
    
    return {
        "total": total_communications,
        "by_type": by_type,
        "by_status": by_status,
        "average_success_rate": avg_success
    }

@admin_router.get("/stats/tests", tags=["Администрирование"])
async def get_tests_stats(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Получение статистики по тестам для администратора."""
    total_tests = db.query(models.MultipleChoiceTest).count()
    active_tests = db.query(models.MultipleChoiceTest).filter(models.MultipleChoiceTest.is_active == True).count()
    
    # Статистика по результатам тестов
    total_results = db.query(models.TestResult).count()
    avg_score = db.query(func.avg(models.TestResult.score)).scalar()
    
    # Распределение по баллам
    score_distribution = {
        "low (0-30%)": db.query(models.TestResult).filter(models.TestResult.score <= 30).count(),
        "medium (31-70%)": db.query(models.TestResult).filter(models.TestResult.score > 30, models.TestResult.score <= 70).count(),
        "high (71-100%)": db.query(models.TestResult).filter(models.TestResult.score > 70).count()
    }
    
    return {
        "tests": {
            "total": total_tests,
            "active": active_tests,
            "inactive": total_tests - active_tests
        },
        "results": {
            "total": total_results,
            "average_score": avg_score,
            "score_distribution": score_distribution
        }
    }

@admin_router.get("/events", tags=["Администрирование"])
async def get_admin_events(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(security.get_current_superuser)
):
    """Получение последних событий для панели администратора."""
    # Последние коммуникации
    recent_communications = db.query(models.Communication).order_by(models.Communication.timestamp.desc()).limit(limit).all()
    
    # Последние результаты тестов
    recent_test_results = db.query(models.TestResult).order_by(models.TestResult.timestamp.desc()).limit(limit).all()
    
    # Новые сотрудники
    new_employees = db.query(models.Employee).order_by(models.Employee.id.desc()).limit(limit).all()
    
    # Новые клиенты
    new_clients = db.query(models.Client).order_by(models.Client.id.desc()).limit(limit).all()
    
    events = []
    
    # Добавляем коммуникации
    for comm in recent_communications:
        events.append({
            "type": "communication",
            "timestamp": comm.timestamp,
            "data": {
                "id": comm.id,
                "client_id": comm.client_id,
                "employee_id": comm.employee_id,
                "call_type": comm.call_type,
                "status": comm.status,
                "success_rate": comm.success_rate
            }
        })
    
    # Добавляем результаты тестов
    for result in recent_test_results:
        events.append({
            "type": "test_result",
            "timestamp": result.timestamp,
            "data": {
                "id": result.id,
                "employee_id": result.employee_id,
                "test_type": result.test_type,
                "score": result.score
            }
        })
    
    # Сортируем события по времени
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return events[:limit]

# Подключаем все маршрутизаторы к основному приложению
app.include_router(auth_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(clients_router, prefix="/api")
app.include_router(communications_router, prefix="/api")
app.include_router(tests_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(chat.router, prefix="/api/chat", tags=["Чат"])

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

    # Определяем группу и уровень стресса на основе среднего балла
    if average_score >= 0.7:
        new_group = "normal"
        new_stress_level = 1  # Норма
    elif average_score >= 0.5:
        new_group = "slightly_below"
        new_stress_level = 2  # Чуть ниже нормы
    else:
        new_group = "significantly_below"
        new_stress_level = 3  # Значительно ниже нормы

    # Обновляем группу и уровень стресса, если они изменились
    if employee.group != new_group or employee.stress_level != new_stress_level:
        employee.group = new_group
        employee.stress_level = new_stress_level
        db.commit()
        db.refresh(employee)
        logger.info(f"Обновлены группа и уровень стресса для сотрудника {employee.id}: группа={new_group}, стресс={new_stress_level}")

@app.post("/api/auth-diagnostic", tags=["debug"])
async def auth_diagnostic(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Диагностический эндпоинт для проверки аутентификации"""
    logger.info(f"Диагностика аутентификации для пользователя: {username}")
    
    # Проверяем сотрудника
    employee = db.query(models.Employee).filter(models.Employee.name == username).first()
    if employee:
        logger.info(f"Найден сотрудник с именем {username}")
        valid = security.verify_password(password, employee.hashed_password)
        logger.info(f"Пароль сотрудника валидный: {valid}")
        return {
            "found": "employee",
            "valid_password": valid,
            "hashed_password_preview": employee.hashed_password[:10] + "..." if employee.hashed_password else None
        }
    
    # Проверяем клиента
    client = db.query(models.Client).filter(models.Client.email == username).first()
    if client:
        logger.info(f"Найден клиент с email {username}")
        valid = security.verify_password(password, client.hashed_password)
        logger.info(f"Пароль клиента валидный: {valid}")
        return {
            "found": "client",
            "valid_password": valid,
            "hashed_password_preview": client.hashed_password[:10] + "..." if client.hashed_password else None
        }
    
    logger.info(f"Пользователь не найден: {username}")
    return {"found": None, "valid_password": False}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True) 