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
                
                # Явно создаем клиента со всеми полями, включая JSON-сериализованные поля
                client = models.Client()
                client.name = client_data["name"]
                client.phone = client_data["phone"]
                client.email = client_data["email"]
                client.hashed_password = hashed_password
                client.preferred_employees = "[]"  # Пустой JSON-массив
                client.blacklisted_employees = "[]"  # Пустой JSON-массив
                
                db.add(client)
                print(f"Создан клиент: {client_data['email']}/{client_data['password']}")

        db.commit()

        # Создаем тестовые коммуникации
        comm_data_list = [
            {
                "client_id": 1,
                "employee_id": 2,  # Иван
                "duration": 300,
                "success_rate": 0.9,
                "call_type": "incoming",
                "status": "completed",
                "notes": "Успешный звонок"
            },
            {
                "client_id": 2,
                "employee_id": 3,  # Мария
                "duration": 180,
                "success_rate": 0.7,
                "call_type": "outgoing",
                "status": "completed",
                "notes": "Средний звонок"
            },
            {
                "client_id": 3,
                "employee_id": 2,  # Иван
                "duration": 0,
                "success_rate": 0.0,
                "call_type": "incoming",
                "status": "missed",
                "notes": "Пропущенный звонок"
            }
        ]

        for data in comm_data_list:
            # Добавляем JSON поля отдельно
            communication = models.Communication()
            communication.client_id = data["client_id"]
            communication.employee_id = data["employee_id"]
            communication.duration = data["duration"]
            communication.success_rate = data["success_rate"]
            communication.call_type = data["call_type"]
            communication.status = data["status"]
            communication.notes = data["notes"]
            communication.client_feedback = "{}"  # Пустой JSON-объект
            communication.employee_feedback = "{}"  # Пустой JSON-объект
            communication.tags = "[]"  # Пустой JSON-массив
            communication.timestamp = datetime.datetime.now()
            
            db.add(communication)
            print(f"Создана коммуникация: {data['client_id']} -> {data['employee_id']}")

        # Создаем тестовый тест
        test_questions = [
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

        if not db.query(models.MultipleChoiceTest).filter(models.MultipleChoiceTest.title == "Тест на стрессоустойчивость").first():
            # Создаем тест по полям
            test_obj = models.MultipleChoiceTest()
            test_obj.title = "Тест на стрессоустойчивость"
            test_obj.description = "Оценка уровня стрессоустойчивости сотрудника"
            test_obj.questions = json.dumps(test_questions)
            test_obj.is_active = True
            
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