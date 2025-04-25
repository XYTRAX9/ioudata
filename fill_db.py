from app.database import SessionLocal, engine
from app import models, security
import datetime
import json

def fill_database():
    db = SessionLocal()
    try:
        # Создаем суперпользователя
        if not db.query(models.Employee).filter(models.Employee.is_superuser == True).first():
            hashed_password = security.get_password_hash("admin123")
            superuser = models.Employee(
                name="admin",
                email="admin@example.com",
                hashed_password=hashed_password,
                stress_level=1,
                group="normal",
                is_active=True,
                is_superuser=True
            )
            db.add(superuser)
            db.commit()
            print("Создан суперпользователь: admin/admin123")

        # Создаем тестовых сотрудников
        employees = [
            {
                "name": "ivan",
                "email": "ivan@example.com",
                "password": "ivan123",
                "stress_level": 2,
                "group": "normal"
            },
            {
                "name": "maria",
                "email": "maria@example.com",
                "password": "maria123",
                "stress_level": 1,
                "group": "slightly_below"
            },
            {
                "name": "alex",
                "email": "alex@example.com",
                "password": "alex123",
                "stress_level": 4,
                "group": "significantly_below"
            }
        ]

        for employee_data in employees:
            if not db.query(models.Employee).filter(models.Employee.name == employee_data["name"]).first():
                hashed_password = security.get_password_hash(employee_data["password"])
                employee = models.Employee(
                    name=employee_data["name"],
                    email=employee_data["email"],
                    hashed_password=hashed_password,
                    stress_level=employee_data["stress_level"],
                    group=employee_data["group"],
                    is_active=True,
                    is_superuser=False
                )
                db.add(employee)
                print(f"Создан сотрудник: {employee_data['name']}/{employee_data['password']}")

        # Создаем тестовых клиентов
        clients = [
            {
                "name": "ООО Компания",
                "phone": "+79001234567",
                "email": "company@example.com",
                "password": "company123"
            },
            {
                "name": "ИП Иванов",
                "phone": "+79001234568",
                "email": "ivanov@example.com",
                "password": "ivanov123"
            },
            {
                "name": "АО Корпорация",
                "phone": "+79001234569",
                "email": "corp@example.com",
                "password": "corp123"
            }
        ]

        for client_data in clients:
            if not db.query(models.Client).filter(models.Client.email == client_data["email"]).first():
                hashed_password = security.get_password_hash(client_data["password"])
                client = models.Client(
                    name=client_data["name"],
                    phone=client_data["phone"],
                    email=client_data["email"],
                    hashed_password=hashed_password,
                    preferred_employees=[],
                    blacklisted_employees=[]
                )
                db.add(client)
                print(f"Создан клиент: {client_data['email']}/{client_data['password']}")

        db.commit()

        # Создаем тестовые коммуникации
        communications = [
            {
                "client_id": 1,
                "employee_id": 2,  # Иван
                "duration": 300,
                "success_rate": 0.9,
                "call_type": "incoming",
                "status": "completed",
                "notes": "Успешный звонок",
                "client_feedback": {"rating": 5, "comment": "Отличный сервис"},
                "employee_feedback": {"stress_level": 2},
                "tags": ["продажи", "консультация"]
            },
            {
                "client_id": 2,
                "employee_id": 3,  # Мария
                "duration": 180,
                "success_rate": 0.7,
                "call_type": "outgoing",
                "status": "completed",
                "notes": "Средний звонок",
                "client_feedback": {"rating": 4, "comment": "Нормально"},
                "employee_feedback": {"stress_level": 2},
                "tags": ["поддержка"]
            },
            {
                "client_id": 3,
                "employee_id": 2,  # Иван
                "duration": 0,
                "success_rate": 0.0,
                "call_type": "incoming",
                "status": "missed",
                "notes": "Пропущенный звонок",
                "client_feedback": {},
                "employee_feedback": {},
                "tags": ["пропущенный"]
            }
        ]

        for comm_data in communications:
            # Создаем новый словарь с JSON-преобразованными данными
            new_comm_data = comm_data.copy()
            new_comm_data["client_feedback"] = json.dumps(comm_data["client_feedback"])
            new_comm_data["employee_feedback"] = json.dumps(comm_data["employee_feedback"])
            new_comm_data["tags"] = json.dumps(comm_data["tags"])
            
            communication = models.Communication(
                **new_comm_data,
                timestamp=datetime.datetime.now()
            )
            db.add(communication)
            print(f"Создана коммуникация: {comm_data['client_id']} -> {comm_data['employee_id']}")

        # Создаем тестовые тесты
        test_data = {
            "title": "Тест на стрессоустойчивость",
            "description": "Оценка уровня стрессоустойчивости сотрудника",
            "questions": [
                {
                    "id": 1,
                    "text": "Как вы реагируете на критику?",
                    "options": [
                        "Спокойно принимаю и анализирую",
                        "Стараюсь не обращать внимания",
                        "Расстраиваюсь, но держу себя в руках",
                        "Сильно переживаю и долго не могу успокоиться"
                    ],
                    "correct_option": 0
                },
                {
                    "id": 2,
                    "text": "Что вы делаете в стрессовой ситуации?",
                    "options": [
                        "Анализирую ситуацию и ищу решение",
                        "Стараюсь отвлечься",
                        "Паникую, но пытаюсь взять себя в руки",
                        "Теряю контроль над ситуацией"
                    ],
                    "correct_option": 0
                }
            ]
        }

        if not db.query(models.MultipleChoiceTest).filter(models.MultipleChoiceTest.title == test_data["title"]).first():
            # Создаем новый словарь с JSON-преобразованными данными
            new_test_data = {
                "title": test_data["title"],
                "description": test_data["description"],
                "questions": json.dumps(test_data["questions"])
            }
            test_obj = models.MultipleChoiceTest(**new_test_data)
            db.add(test_obj)
            print("Создан тест на стрессоустойчивость")

        db.commit()
        print("\nБаза данных успешно заполнена тестовыми данными!")

    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем таблицы
    models.Base.metadata.create_all(bind=engine)
    # Заполняем базу данных
    fill_database() 