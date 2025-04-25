from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    stress_level = Column(Integer, default=1)  # 1-5, где 5 - максимальный стресс
    group = Column(String, default="normal")  # "normal", "slightly_below", "significantly_below"
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    test_results = relationship("TestResult", back_populates="employee")
    communications = relationship("Communication", back_populates="employee")

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    test_type = Column(String)  # "audio", "video", "questionnaire", "multiple_choice"
    score = Column(Float)  # 0-1, где 1 - максимальный результат
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(JSON)  # JSON объект с деталями теста
    employee = relationship("Employee", back_populates="test_results")

class MultipleChoiceTest(Base):
    __tablename__ = "multiple_choice_tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    questions = Column(JSON)  # Список вопросов с вариантами ответов и ID
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Убедимся, что вопросы имеют ID
        if self.questions:
            for i, question in enumerate(self.questions):
                if "id" not in question:
                    question["id"] = i + 1

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Добавляем поле для хранения пароля
    communication_history = relationship("Communication", back_populates="client")
    preferred_employees = Column(JSON, default=list)  # Список ID предпочитаемых сотрудников
    blacklisted_employees = Column(JSON, default=list)  # Список ID сотрудников, с которыми не хотят общаться

class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    duration = Column(Integer)  # Длительность звонка в секундах
    success_rate = Column(Float)  # 0-1, где 1 - максимальный успех
    call_type = Column(String)  # "incoming", "outgoing"
    status = Column(String)  # "completed", "missed", "rejected"
    notes = Column(Text)  # Заметки о звонке
    client_feedback = Column(JSON)  # Отзыв клиента
    employee_feedback = Column(JSON)  # Отзыв сотрудника
    tags = Column(JSON, default=list)  # Теги для категоризации звонка
    details = Column(JSON, default=lambda: {"messages": []}) # Добавлено поле для сообщений чата
    client = relationship("Client", back_populates="communication_history")
    employee = relationship("Employee", back_populates="communications") 