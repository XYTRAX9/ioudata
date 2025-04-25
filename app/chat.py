from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends, status, Form, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List, Optional, Tuple, Set
import json
from datetime import datetime
import aiohttp
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
import os
import asyncio

from . import models, schemas, security, crud
from .database import SessionLocal, engine

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

# Настройка шаблонов
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

class LoginData(BaseModel):
    username: str
    password: str

class ChatFeedback(BaseModel):
    rating: int
    comment: str
    tags: List[str]

# Максимальный уровень стресса, при котором оператор может обрабатывать чаты
MAX_STRESS_LEVEL_FOR_CHAT = 2

class ConnectionManager:
    def __init__(self):
        # Активные клиентские соединения: client_id -> WebSocket
        self.active_clients: Dict[int, WebSocket] = {}
        
        # Активные соединения операторов: operator_id -> WebSocket
        self.active_operators: Dict[int, WebSocket] = {}
        
        # Связь между клиентами и операторами: client_id -> operator_id
        self.client_operator_mapping: Dict[int, int] = {}
        
        # Обратное отображение: operator_id -> Set[client_id]
        self.operator_clients_mapping: Dict[int, Set[int]] = {}
        
        # Отслеживание коммуникаций для чатов: client_id -> communication_id
        self.chat_communications: Dict[int, int] = {}
        
        # Блокировка для синхронизации
        self.lock = asyncio.Lock()

    async def connect_client(self, client_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_clients[client_id] = websocket
        logger.info(f"Клиент {client_id} подключен")

    async def connect_operator(self, operator_id: int, websocket: WebSocket, db: Session):
        # Проверяем уровень стресса оператора
        operator = crud.get_employee(db, operator_id)
        if not operator:
            await websocket.close(code=4001, reason="Оператор не найден")
            return False
        
        # Если уровень стресса оператора слишком высокий
        if operator.stress_level > MAX_STRESS_LEVEL_FOR_CHAT:
            await websocket.close(code=4003, reason="Стрессовый уровень слишком высокий")
            return False
        
        await websocket.accept()
        self.active_operators[operator_id] = websocket
        
        # Инициализация отображения оператор -> клиенты
        if operator_id not in self.operator_clients_mapping:
            self.operator_clients_mapping[operator_id] = set()
            
        logger.info(f"Оператор {operator_id} подключен, уровень стресса: {operator.stress_level}")
        return True

    async def disconnect_client(self, client_id: int):
        if client_id in self.active_clients:
            del self.active_clients[client_id]
            
            # Уведомляем оператора о отключении клиента
            if client_id in self.client_operator_mapping:
                operator_id = self.client_operator_mapping[client_id]
                await self.send_to_operator(operator_id, {
                    "type": "client_disconnect",
                    "client_id": client_id
                })
                
                # Обновляем отображение оператор -> клиенты
                if operator_id in self.operator_clients_mapping:
                    self.operator_clients_mapping[operator_id].discard(client_id)
                
                # Удаляем связь клиент -> оператор
                del self.client_operator_mapping[client_id]
                
            logger.info(f"Клиент {client_id} отключен")

    async def disconnect_operator(self, operator_id: int):
        if operator_id in self.active_operators:
            del self.active_operators[operator_id]
            
            # Уведомляем всех клиентов этого оператора
            if operator_id in self.operator_clients_mapping:
                for client_id in list(self.operator_clients_mapping[operator_id]):
                    if client_id in self.active_clients:
                        await self.send_to_client(client_id, {
                            "type": "operator_disconnect",
                            "message": "Оператор отключился от чата"
                        })
                        
                        # Удаляем связь клиент -> оператор
                        if client_id in self.client_operator_mapping:
                            del self.client_operator_mapping[client_id]
                
                # Очищаем список клиентов оператора
                self.operator_clients_mapping[operator_id] = set()
                
            logger.info(f"Оператор {operator_id} отключен")

    async def send_to_client(self, client_id: int, message: dict):
        if client_id in self.active_clients:
            await self.active_clients[client_id].send_json(message)
            logger.debug(f"Сообщение отправлено клиенту {client_id}")

    async def send_to_operator(self, operator_id: int, message: dict):
        if operator_id in self.active_operators:
            logger.info(f"Отправка JSON оператору {operator_id}: {json.dumps(message)}")
            await self.active_operators[operator_id].send_json(message)
            logger.debug(f"Сообщение отправлено оператору {operator_id}")
        else:
            logger.warning(f"Оператор {operator_id} не активен. Сообщение не отправлено.")

    async def assign_operator_to_client(self, client_id: int, operator_id: int, client_name: str, db: Session, communication_id: int):
        async with self.lock:
            # Устанавливаем связь между клиентом и оператором
            self.client_operator_mapping[client_id] = operator_id
            
            # Добавляем клиента в список оператора
            if operator_id not in self.operator_clients_mapping:
                self.operator_clients_mapping[operator_id] = set()
            self.operator_clients_mapping[operator_id].add(client_id)
            
            # Уведомляем оператора о новом клиенте
            await self.send_to_operator(operator_id, {
            "type": "new_client",
            "client_id": client_id,
            "client_name": client_name
        })
            
            # Уведомляем клиента о подключении к оператору
            operator = crud.get_employee(db, operator_id)
            await self.send_to_client(client_id, {
                "type": "operator_assigned",
                "operator_name": operator.name if operator else "Оператор поддержки",
                "communication_id": communication_id
            })
            
            logger.info(f"Оператор {operator_id} назначен клиенту {client_id}")

    async def broadcast_client_message(self, client_id: int, message: str, db: Session):
        if client_id in self.client_operator_mapping:
            operator_id = self.client_operator_mapping[client_id]
            
            # Обновляем запись о коммуникации (если есть)
            if client_id in self.chat_communications:
                comm_id = self.chat_communications[client_id]
                logger.info(f"Вызов add_message_to_communication для клиента {client_id}, comm_id {comm_id}")
                try:
                    added = crud.add_message_to_communication(db, comm_id, "client", message)
                    logger.info(f"add_message_to_communication для клиента {client_id} вернуло: {added}")
                except Exception as e:
                     logger.error(f"Ошибка при вызове add_message_to_communication для клиента {client_id}, comm_id {comm_id}: {str(e)}", exc_info=True)

            # Получаем имя клиента
            client = crud.get_client(db, client_id)
            client_name = client.name if client else f"Клиент {client_id}"
            
            # Отправляем сообщение оператору
            await self.send_to_operator(operator_id, {
                "type": "message",
                "client_id": client_id,
                "client_name": client_name,
                "message": message
            })
            
            logger.debug(f"Сообщение от клиента {client_id} доставлено оператору {operator_id}")
            return True
        else:
             logger.warning(f"Не найдена связь оператор-клиент для клиента {client_id} в broadcast_client_message.")
             return False

    async def broadcast_operator_message(self, operator_id: int, client_id: int, message: str, db: Session):
        # Проверяем, что оператор действительно связан с этим клиентом
        if client_id in self.client_operator_mapping and self.client_operator_mapping[client_id] == operator_id:
            # Обновляем запись о коммуникации (если есть)
            if client_id in self.chat_communications:
                comm_id = self.chat_communications[client_id]
                logger.info(f"Вызов add_message_to_communication для оператора {operator_id}, comm_id {comm_id}")
                try:
                    added = crud.add_message_to_communication(db, comm_id, "employee", message)
                    logger.info(f"add_message_to_communication для оператора {operator_id} вернуло: {added}")
                except Exception as e:
                     logger.error(f"Ошибка при вызове add_message_to_communication для оператора {operator_id}, comm_id {comm_id}: {str(e)}", exc_info=True)

            # Получаем имя оператора
            operator = crud.get_employee(db, operator_id)
            operator_name = operator.name if operator else "Оператор поддержки"
            
            # Отправляем сообщение клиенту
            await self.send_to_client(client_id, {
                "type": "message",
                "sender": "operator",
                "operator_name": operator_name,
                "message": message
            })
            
            logger.debug(f"Сообщение от оператора {operator_id} доставлено клиенту {client_id}")
            return True
        return False

    async def handle_feedback(self, client_id: int, rating: int, comment: str, tags: List[str], db: Session):
        if client_id not in self.chat_communications:
            logger.warning(f"Не найдена запись коммуникации для клиента {client_id}")
            return False
        
        comm_id = self.chat_communications[client_id]
        
        # Обновляем запись о коммуникации с обратной связью
        communication = crud.update_communication_feedback(
            db, 
            comm_id,
            client_feedback={
                "rating": rating,
                "comment": comment,
                "tags": tags
            }
        )
        
        if not communication:
            logger.warning(f"Не удалось обновить обратную связь для коммуникации {comm_id}")
            return False
        
        # Обновляем статус коммуникации на "завершено"
        crud.update_communication_status(db, comm_id, "completed")
        
        # Если рейтинг низкий (1-2), увеличиваем уровень стресса оператора
        if rating <= 2 and communication.employee_id:
            operator_id = communication.employee_id
            operator = crud.get_employee(db, operator_id)
            
            if operator:
                new_stress_level = min(5, operator.stress_level + 1)
                crud.update_employee_stress_level(db, operator_id, new_stress_level)
                logger.info(f"Уровень стресса оператора {operator_id} увеличен до {new_stress_level} из-за низкого рейтинга")
                
                # Если новый уровень стресса выше допустимого, уведомляем оператора
                if new_stress_level > MAX_STRESS_LEVEL_FOR_CHAT and operator_id in self.active_operators:
                    await self.send_to_operator(operator_id, {
                        "type": "stress_limit",
                        "message": "Ваш уровень стресса превысил допустимый предел. Пожалуйста, сделайте перерыв."
                    })
        
        # Если рейтинг высокий (4-5), уменьшаем уровень стресса оператора
        elif rating >= 4 and communication.employee_id:
            operator_id = communication.employee_id
            operator = crud.get_employee(db, operator_id)
            
            if operator:
                new_stress_level = max(1, operator.stress_level - 1)
                crud.update_employee_stress_level(db, operator_id, new_stress_level)
                logger.info(f"Уровень стресса оператора {operator_id} уменьшен до {new_stress_level} благодаря высокому рейтингу")
        
        logger.info(f"Обратная связь для коммуникации {comm_id} успешно обработана, рейтинг: {rating}")
        return True

connection_manager = ConnectionManager()

# Хранение истории сообщений
chat_history: List[Dict] = []

# Хранение активных чатов
active_chats: Dict[str, str] = {}  # client_id -> operator_id

# Хранение токенов
operator_tokens: Dict[str, str] = {}  # support_id -> token
client_tokens: Dict[str, str] = {}  # client_id -> token

async def get_available_operator(db: Session) -> Optional[int]:
    """
    Получить ID доступного оператора с низким уровнем стресса.
    """
    # Получаем всех операторов с низким уровнем стресса (1-2), которые сейчас в сети
    available_operators = crud.get_employees_by_stress_level(db, max_level=MAX_STRESS_LEVEL_FOR_CHAT)
    
    # Фильтруем только тех, кто сейчас онлайн
    online_operators = [op for op in available_operators if op.id in connection_manager.active_operators]
    
    if not online_operators:
        logger.warning("Нет доступных операторов с подходящим уровнем стресса")
        return None # Возвращаем None, если операторов нет
    
    # Выбираем оператора с наименьшим количеством активных клиентов
    selected_operator = min(
        online_operators,
        key=lambda op: len(connection_manager.operator_clients_mapping.get(op.id, set()))
    )
    
    # Убрано создание Communication
    
    logger.info(f"Выбран оператор {selected_operator.id} (уровень стресса: {selected_operator.stress_level})")
    return selected_operator.id # Возвращаем только ID

@router.get("/client", response_class=HTMLResponse)
async def get_client_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.get("/support", response_class=HTMLResponse)
async def get_support_chat(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

@router.post("/client/login")
async def client_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Используем username как email для клиентов
    client = crud.authenticate_client(db, form_data.username, form_data.password)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    
    return {"client_id": client.id, "name": client.name}

@router.post("/support/login")
async def support_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Попытка входа оператора с именем: {form_data.username}")
    
    # Проверяем, существует ли сотрудник с таким именем в БД
    employee = db.query(models.Employee).filter(models.Employee.name == form_data.username).first()
    if not employee:
        logger.warning(f"Оператор с именем {form_data.username} не найден в базе данных")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
    
    logger.info(f"Оператор найден: {employee.name} (ID: {employee.id}), проверяем пароль")
    
    # Проверяем пароль
    if not security.verify_password(form_data.password, employee.hashed_password):
        logger.warning(f"Неверный пароль для оператора {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
    
    # Проверяем уровень стресса сотрудника
    logger.info(f"Проверка уровня стресса оператора: {employee.stress_level}")
    if employee.stress_level > MAX_STRESS_LEVEL_FOR_CHAT:
        logger.warning(f"Уровень стресса оператора {form_data.username} слишком высок: {employee.stress_level} > {MAX_STRESS_LEVEL_FOR_CHAT}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ запрещен. Ваш уровень стресса ({employee.stress_level}) слишком высок. Только сотрудники с уровнем стресса не выше {MAX_STRESS_LEVEL_FOR_CHAT} могут использовать чат.",
        )
    
    logger.info(f"Успешный вход оператора: {employee.name} (ID: {employee.id})")
    return {"operator_id": employee.id, "name": employee.name, "stress_level": employee.stress_level}

@router.websocket("/ws/client/{client_id}")
async def websocket_client_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    # Проверяем, что клиент существует
    client = crud.get_client(db, client_id)
    if not client:
        await websocket.close(code=4001)
        logger.warning(f"Попытка подключения несуществующего клиента: {client_id}")
        return

    # Подключаем клиента
    await connection_manager.connect_client(client_id, websocket)
    
    try:
        # Находим доступного оператора
        operator_id = await get_available_operator(db) # Получаем только ID
        
        if operator_id is None:
            await websocket.send_json({
                "type": "error",
                "message": "Все операторы заняты. Пожалуйста, попробуйте позже."
            })
            await websocket.close()
            return
            
        # Создаем запись Communication ЗДЕСЬ, после нахождения оператора
        communication = models.Communication(
            client_id=client_id,        # Указываем client_id
            employee_id=operator_id,    # Указываем employee_id
            call_type="chat",
            status="active",
            timestamp=datetime.now(),
            # Используем {} для JSON полей
            client_feedback={},
            employee_feedback={}
            # tags использует default=list из модели
        )
        db.add(communication)
        try:
            db.commit()
            db.refresh(communication)
            logger.info(f"Создана запись Communication {communication.id} для клиента {client_id} и оператора {operator_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Ошибка при сохранении Communication для клиента {client_id}: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": "Ошибка сервера при создании чата. Попробуйте позже."
            })
            await websocket.close()
            return
        
        # Сохраняем ID коммуникации
        connection_manager.chat_communications[client_id] = communication.id
        
        # Назначаем оператора клиенту
        await connection_manager.assign_operator_to_client(client_id, operator_id, client.name, db, communication.id)
        
        # Обрабатываем сообщения
        while True:
            data = await websocket.receive_json()
            
            if "message" in data:
                # Отправляем сообщение оператору
                success = await connection_manager.broadcast_client_message(client_id, data["message"], db)
                if not success:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Не удалось доставить сообщение оператору"
                    })
            
            elif "feedback" in data:
                # Обрабатываем обратную связь
                feedback = data["feedback"]
                success = await connection_manager.handle_feedback(
                    client_id,
                    rating=feedback.get("rating", 3),
                    comment=feedback.get("comment", ""),
                    tags=feedback.get("tags", []),
                    db=db
                )
                
                if success:
                    await websocket.send_json({
                        "type": "feedback_received",
                        "message": "Спасибо за вашу обратную связь!"
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Не удалось обработать обратную связь"
                    })
    
    except WebSocketDisconnect:
        logger.info(f"Клиент {client_id} отключился")
    except Exception as e:
        # Улучшенное логирование с traceback
        logger.error(f"Произошла ошибка в websocket_client_endpoint для клиента {client_id}", exc_info=True)
    finally:
        # Отключаем клиента
        await connection_manager.disconnect_client(client_id)

@router.websocket("/ws/support/{operator_id}")
async def websocket_support_endpoint(websocket: WebSocket, operator_id: int, db: Session = Depends(get_db)):
    # Подключаем оператора
    success = await connection_manager.connect_operator(operator_id, websocket, db)
    if not success:
        # Соединение было закрыто в connect_operator
        return

    try:
        # Обрабатываем сообщения
        while True:
            data = await websocket.receive_json()
            
            if "message" in data and "client_id" in data:
                client_id = data["client_id"]
                # Отправляем сообщение клиенту
                success = await connection_manager.broadcast_operator_message(
                    operator_id, client_id, data["message"], db
                )
                
                if not success:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Не удалось доставить сообщение клиенту"
                    })
    
    except WebSocketDisconnect:
        logger.info(f"Оператор {operator_id} отключился")
    except Exception as e:
         # Улучшенное логирование с traceback
        logger.error(f"Произошла ошибка в websocket_support_endpoint для оператора {operator_id}", exc_info=True)
    finally:
        # Отключаем оператора
        await connection_manager.disconnect_operator(operator_id)

# Добавление функций для CRUD-операций с записями о коммуникациях
def add_crud_routes():
    @router.post("/communications/feedback/{comm_id}")
    async def update_communication_feedback(
        comm_id: int, 
        client_feedback: Optional[dict] = None,
        employee_feedback: Optional[dict] = None,
        db: Session = Depends(get_db)
    ):
        """Обновить обратную связь для коммуникации"""
        try:
            communication = crud.update_communication_feedback(
                db, comm_id, client_feedback, employee_feedback
            )
            
            if not communication:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Коммуникация {comm_id} не найдена"
                )
            
            return {"success": True, "communication_id": comm_id}
        except Exception as e:
            logger.error(f"Ошибка при обновлении обратной связи для коммуникации {comm_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении обратной связи: {str(e)}"
            )

    @router.post("/feedback/{comm_id}")
    async def submit_chat_feedback(
        comm_id: int,
        feedback: dict = Body(...),
        db: Session = Depends(get_db)
    ):
        """Обработка обратной связи от клиента по чату"""
        try:
            communication = crud.update_communication_feedback(
                db, comm_id, client_feedback=feedback
            )
            
            if not communication:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Коммуникация {comm_id} не найдена"
                )
            
            # Обновляем статус коммуникации на "завершено"
            crud.update_communication_status(db, comm_id, "completed")
            
            # Обрабатываем рейтинг и изменение стресса оператора
            if communication.employee_id and "rating" in feedback:
                rating = feedback["rating"]
                operator_id = communication.employee_id
                operator = crud.get_employee(db, operator_id)
                
                if operator:
                    if rating <= 2:
                        # Низкий рейтинг - увеличиваем стресс
                        new_stress_level = min(5, operator.stress_level + 1)
                        crud.update_employee_stress_level(db, operator_id, new_stress_level)
                        logger.info(f"Уровень стресса оператора {operator_id} увеличен до {new_stress_level} из-за низкого рейтинга")
                    elif rating >= 4:
                        # Высокий рейтинг - уменьшаем стресс
                        new_stress_level = max(1, operator.stress_level - 1)
                        crud.update_employee_stress_level(db, operator_id, new_stress_level)
                        logger.info(f"Уровень стресса оператора {operator_id} уменьшен до {new_stress_level} благодаря высокому рейтингу")
            
            return {"success": True, "communication_id": comm_id}
        except Exception as e:
            logger.error(f"Ошибка при обработке обратной связи для коммуникации {comm_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обработке обратной связи: {str(e)}"
            )

add_crud_routes()

@router.get("/history/{client_id}", response_model=List[Dict])
async def get_chat_history(client_id: int, db: Session = Depends(get_db)):
    """Получение истории сообщений последнего чата для клиента."""
    # Находим последнюю коммуникацию типа 'chat' для данного клиента
    last_communication = db.query(models.Communication).filter(
        models.Communication.client_id == client_id,
        models.Communication.call_type == "chat" 
    ).order_by(models.Communication.timestamp.desc()).first()

    if last_communication and last_communication.details and "messages" in last_communication.details:
        # Возвращаем список сообщений из поля details
        return last_communication.details.get("messages", [])
    else:
        # Если коммуникация не найдена или поле details пустое/не содержит messages, возвращаем пустой список
        logger.info(f"Не найдена история чата для клиента {client_id}")
        return []

@router.get("/active")
async def get_active_chats():
    """Получение списка активных чатов"""
    return active_chats 

@router.get("/communication/{client_id}")
async def get_communication_id(client_id: str):
    """Получение ID коммуникации для клиента"""
    if client_id in connection_manager.chat_communications:
        return {"communication_id": connection_manager.chat_communications[int(client_id)]}
    else:
        raise HTTPException(status_code=404, detail="No active communication found for this client") 