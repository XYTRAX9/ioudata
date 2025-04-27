from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import logging
from . import models, schemas, security

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функции для работы с сотрудниками
def get_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
    """Получение сотрудника по ID"""
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employee_by_email(db: Session, email: str) -> Optional[models.Employee]:
    """Получение сотрудника по email"""
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[models.Employee]:
    """Получение списка всех сотрудников"""
    return db.query(models.Employee).offset(skip).limit(limit).all()

def get_employees_by_stress_level(db: Session, max_level: int = 2) -> List[models.Employee]:
    """Получение списка сотрудников с уровнем стресса не выше указанного"""
    return db.query(models.Employee).filter(
        models.Employee.is_active == True,
        models.Employee.stress_level <= max_level
    ).order_by(models.Employee.stress_level.asc()).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    """Создание нового сотрудника"""
    hashed_password = security.get_password_hash(employee.password)
    db_employee = models.Employee(
        **employee.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee_stress_level(db: Session, employee_id: int, stress_level: int) -> models.Employee:
    """Обновление уровня стресса сотрудника"""
    employee = get_employee(db, employee_id)
    if not employee:
        return None
    
    # Проверяем, что уровень стресса в допустимых пределах (1-5)
    stress_level = max(1, min(5, stress_level))
    
    employee.stress_level = stress_level
    db.commit()
    db.refresh(employee)
    return employee

def authenticate_employee(db: Session, name: str, password: str) -> Optional[models.Employee]:
    """Аутентификация сотрудника"""
    employee = db.query(models.Employee).filter(models.Employee.name == name).first()
    if not employee:
        return None
    if not security.verify_password(password, employee.hashed_password):
        return None
    return employee

# Функции для работы с клиентами
def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    """Получение клиента по ID"""
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_client_by_email(db: Session, email: str) -> Optional[models.Client]:
    """Получение клиента по email"""
    return db.query(models.Client).filter(models.Client.email == email).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Client]:
    """Получение списка всех клиентов"""
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    """Создание нового клиента"""
    hashed_password = security.get_password_hash(client.password)
    db_client = models.Client(
        **client.model_dump(exclude={"password"}),
        hashed_password=hashed_password
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def authenticate_client(db: Session, email: str, password: str) -> Optional[models.Client]:
    """Аутентификация клиента по email"""
    logger.info(f"Попытка аутентификации клиента с email: {email}")
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        logger.warning(f"Клиент с email {email} не найден")
        return None
    
    password_verified = security.verify_password(password, client.hashed_password)
    logger.info(f"Проверка пароля для клиента {email}: {'успешно' if password_verified else 'неудачно'}")
    
    if not password_verified:
        return None
    
    logger.info(f"Клиент {email} успешно аутентифицирован")
    return client

# Функции для работы с коммуникациями
def get_communication(db: Session, communication_id: int) -> Optional[models.Communication]:
    """Получение коммуникации по ID"""
    return db.query(models.Communication).filter(models.Communication.id == communication_id).first()

def get_communications(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    client_id: Optional[int] = None,
    employee_id: Optional[int] = None
) -> List[models.Communication]:
    """Получение списка коммуникаций с возможностью фильтрации"""
    query = db.query(models.Communication)
    if client_id:
        query = query.filter(models.Communication.client_id == client_id)
    if employee_id:
        query = query.filter(models.Communication.employee_id == employee_id)
    return query.offset(skip).limit(limit).all()

def create_communication(db: Session, communication: schemas.CommunicationCreate) -> models.Communication:
    """Создание новой коммуникации"""
    db_communication = models.Communication(
        **communication.model_dump(),
        timestamp=datetime.now()
    )
    db.add(db_communication)
    db.commit()
    db.refresh(db_communication)
    return db_communication

def add_message_to_communication(db: Session, communication_id: int, sender_type: str, message: str) -> bool:
    """
    Добавление сообщения к коммуникации
    sender_type: "employee" или "client"
    """
    communication = get_communication(db, communication_id)
    if not communication:
        logger.warning(f"Не найдена коммуникация с ID {communication_id}")
        return False
    
    try:
        # 1. Читаем текущие детали (или создаем пустой, если их нет)
        current_details = communication.details if communication.details else {}
        # 2. Получаем текущий список сообщений (или пустой, если ключа нет)
        current_messages = current_details.get("messages", [])
        
        # 3. Создаем новое сообщение
        new_message = {
            "sender": sender_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # 4. Создаем НОВЫЙ список сообщений, добавляя новое
        new_messages_list = current_messages + [new_message]
        
        # 5. Создаем НОВЫЙ словарь details
        new_details_dict = {"messages": new_messages_list}
        
        # 6. Присваиваем новый словарь полю details
        communication.details = new_details_dict
        
        # Оставим flag_modified на всякий случай, хотя теперь он может быть излишним
        flag_modified(communication, "details") 
        
        logger.info(f"Перед коммитом для comm_id {communication_id}. Session active: {db.is_active}. Dirty: {db.dirty}")
        db.commit()
        logger.info(f"После коммита для comm_id {communication_id}.")
        
        logger.info(f"Сообщение добавлено к коммуникации {communication_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении сообщения к коммуникации {communication_id}: {str(e)}")
        db.rollback()
        return False

def update_communication_status(db: Session, communication_id: int, status: str) -> Optional[models.Communication]:
    """Обновление статуса коммуникации"""
    communication = get_communication(db, communication_id)
    if not communication:
        logger.warning(f"Не найдена коммуникация с ID {communication_id}")
        return None
    
    valid_statuses = ["active", "completed", "failed"]
    if status not in valid_statuses:
        logger.warning(f"Недопустимый статус: {status}")
        return None
    
    communication.status = status
    db.commit()
    db.refresh(communication)
    
    logger.info(f"Статус коммуникации {communication_id} обновлен на '{status}'")
    return communication

def update_communication_feedback(
    db: Session, 
    communication_id: int, 
    client_feedback: Optional[Dict[str, Any]] = None,
    employee_feedback: Optional[Dict[str, Any]] = None
) -> Optional[models.Communication]:
    """Обновление отзыва о коммуникации"""
    communication = get_communication(db, communication_id)
    if not communication:
        logger.warning(f"Не найдена коммуникация с ID {communication_id}")
        return None
    
    try:
        # Обновляем отзыв клиента
        if client_feedback is not None:
            communication.client_feedback = client_feedback
        
        # Обновляем отзыв сотрудника
        if employee_feedback is not None:
            communication.employee_feedback = employee_feedback
        
        db.commit()
        db.refresh(communication)
        
        logger.info(f"Отзыв о коммуникации {communication_id} обновлен")
        return communication
    except Exception as e:
        logger.error(f"Ошибка при обновлении отзыва о коммуникации {communication_id}: {str(e)}")
        db.rollback()
        return None

# Функции для работы с тестами
def get_test_results(db: Session, employee_id: int) -> List[models.TestResult]:
    """Получение результатов тестов сотрудника"""
    return db.query(models.TestResult).filter(
        models.TestResult.employee_id == employee_id
    ).order_by(models.TestResult.timestamp.desc()).all()

def create_test_result(db: Session, test_result: schemas.TestResultCreate) -> models.TestResult:
    """Создание нового результата теста"""
    db_test_result = models.TestResult(
        **test_result.model_dump(),
        timestamp=datetime.now()
    )
    db.add(db_test_result)
    db.commit()
    db.refresh(db_test_result)
    return db_test_result 