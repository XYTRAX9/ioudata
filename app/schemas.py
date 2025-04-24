from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str
    stress_level: float
    group: str

class EmployeeCreate(EmployeeBase):
    password: str

class Employee(EmployeeBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

class EmployeeInDB(Employee):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    name: Optional[str] = None

class TestResultBase(BaseModel):
    test_type: str
    score: float
    details: Dict[str, Any]

class TestResultCreate(TestResultBase):
    employee_id: int

class TestResult(TestResultBase):
    id: int
    employee_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    id: Optional[int] = None
    text: str
    options: List[str]
    correct_option: int  # Индекс правильного ответа (0-3)

class MultipleChoiceTestBase(BaseModel):
    title: str
    description: str
    questions: List[QuestionBase]

class MultipleChoiceTestCreate(MultipleChoiceTestBase):
    pass

class MultipleChoiceTest(MultipleChoiceTestBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class TestAnswer(BaseModel):
    question_id: int
    selected_option: int  # Индекс выбранного ответа (0-3)

class TestSubmission(BaseModel):
    test_id: int
    answers: List[TestAnswer]

class AudioTestRequest(BaseModel):
    audio_file_url: str

class VideoTestRequest(BaseModel):
    video_file_url: str

class QuestionnaireRequest(BaseModel):
    answers: Dict[str, Any]

class ClientBase(BaseModel):
    name: str
    phone: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    preferred_employees: List[int] = []
    blacklisted_employees: List[int] = []

    class Config:
        from_attributes = True

class CommunicationBase(BaseModel):
    client_id: int
    employee_id: int
    duration: Optional[int] = None
    success_rate: float
    call_type: str
    status: str
    notes: Optional[str] = None
    client_feedback: Optional[Dict[str, Any]] = None
    employee_feedback: Optional[Dict[str, Any]] = None
    tags: List[str] = []

class CommunicationCreate(CommunicationBase):
    pass

class Communication(CommunicationBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class CommunicationUpdate(BaseModel):
    duration: Optional[int] = None
    success_rate: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    client_feedback: Optional[Dict[str, Any]] = None
    employee_feedback: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None 