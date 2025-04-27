import logging
import os
import sqlite3
import json
from datetime import datetime, timedelta
from . import security

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    db_path = "matching_system.db"
    
    logger.info("Создание базы данных...")
    
    # Проверяем, существует ли файл базы данных
    if not os.path.exists(db_path):
        logger.info(f"Файл базы данных {db_path} не существует, создаем новый")
    
    # Создаем базу данных и таблицы напрямую через SQL
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу employees
        logger.info("Создание таблицы employees...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL,
            hashed_password VARCHAR(100) NOT NULL,
            stress_level INTEGER NOT NULL DEFAULT 1,
            "group" VARCHAR(50) NOT NULL DEFAULT 'normal',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            is_superuser BOOLEAN NOT NULL DEFAULT 0
        )
        ''')
        
        # Создаем таблицу test_results
        logger.info("Создание таблицы test_results...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            test_type VARCHAR(50) NOT NULL,
            score REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')
        
        # Создаем таблицу multiple_choice_tests
        logger.info("Создание таблицы multiple_choice_tests...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS multiple_choice_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            questions TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
        ''')
        
        # Создаем таблицу clients
        logger.info("Создание таблицы clients...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) UNIQUE,
            email VARCHAR(100) UNIQUE,
            hashed_password VARCHAR(100) NOT NULL,
            preferred_employees TEXT DEFAULT '[]',
            blacklisted_employees TEXT DEFAULT '[]',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Проверяем, существует ли колонка details в таблице communications
        cursor.execute("PRAGMA table_info(communications)")
        columns = cursor.fetchall()
        has_details_column = any(column[1] == 'details' for column in columns)
        
        # Создаем таблицу communications
        logger.info("Создание таблицы communications...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            success_rate REAL,
            call_type VARCHAR(20),
            status VARCHAR(20),
            notes TEXT,
            client_feedback TEXT,
            employee_feedback TEXT,
            tags TEXT DEFAULT '[]',
            details TEXT DEFAULT '{"messages":[]}',
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')
        
        # Добавляем колонку details, если она отсутствует
        if not has_details_column:
            try:
                logger.info("Добавление колонки details в таблицу communications...")
                cursor.execute('''
                ALTER TABLE communications 
                ADD COLUMN details TEXT DEFAULT '{"messages":[]}'
                ''')
                logger.info("Колонка details успешно добавлена")
            except sqlite3.OperationalError as e:
                logger.warning(f"Не удалось добавить колонку details: {e}")
        
        # Проверяем, существует ли суперпользователь
        cursor.execute("SELECT COUNT(*) FROM employees WHERE name = 'admin'")
        if cursor.fetchone()[0] == 0:
            logger.info("Создаем суперпользователя admin")
            hashed_password = security.get_password_hash("admin123")
            cursor.execute('''
            INSERT INTO employees (name, email, hashed_password, stress_level, "group", is_active, is_superuser)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@example.com', hashed_password, 1, 'normal', 1, 1))
            logger.info("Создан суперпользователь admin")
        else:
            logger.info("Суперпользователь admin уже существует")
        
        # Проверяем, существует ли оператор поддержки
        cursor.execute("SELECT COUNT(*) FROM employees WHERE name = 'support'")
        if cursor.fetchone()[0] == 0:
            logger.info("Создаем оператора поддержки")
            hashed_password = security.get_password_hash("support123")
            cursor.execute('''
            INSERT INTO employees (name, email, hashed_password, stress_level, "group", is_active, is_superuser)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('support', 'support@example.com', hashed_password, 1, 'normal', 1, 0))
            logger.info("Создан оператор поддержки 'support'")
        else:
            logger.info("Оператор поддержки 'support' уже существует")
            # Обновляем группу оператора поддержки на normal, если она была support
            cursor.execute('''
            UPDATE employees 
            SET "group" = 'normal' 
            WHERE name = 'support' AND "group" = 'support'
            ''')
            if cursor.rowcount > 0:
                logger.info("Обновлена группа оператора поддержки с 'support' на 'normal'")
        
        # Проверяем, существует ли тестовый клиент
        cursor.execute("SELECT COUNT(*) FROM clients WHERE email = 'client@example.com'")
        if cursor.fetchone()[0] == 0:
            logger.info("Создаем тестового клиента")
            hashed_password = security.get_password_hash("client123")
            cursor.execute('''
            INSERT INTO clients (name, phone, email, hashed_password, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ('Тестовый Клиент', '+7-999-999-9999', 'client@example.com', hashed_password, datetime.now(), 1))
            logger.info("Создан тестовый клиент")
        else:
            logger.info("Тестовый клиент уже существует")

        # Проверяем, существуют ли записи в таблице multiple_choice_tests
        cursor.execute("SELECT COUNT(*) FROM multiple_choice_tests")
        if cursor.fetchone()[0] == 0:
            logger.info("Создаем примеры тестов...")
            
            test1 = {
                "title": "Тест по навыкам обслуживания клиентов",
                "description": "Базовый тест для оценки навыков работы с клиентами",
                "questions": [
                    {
                        "id": 1,
                        "text": "Как лучше всего начать разговор с клиентом?",
                        "options": [
                            "Спросить, что ему нужно",
                            "Поздороваться и представиться",
                            "Сразу перейти к решению проблемы",
                            "Попросить контактные данные"
                        ],
                        "correct_option": 1
                    },
                    {
                        "id": 2,
                        "text": "Что делать, если клиент раздражен?",
                        "options": [
                            "Говорить громче, чтобы он услышал решение",
                            "Сохранять спокойствие и выслушать его проблему",
                            "Перевести на другого оператора",
                            "Предложить перезвонить позже"
                        ],
                        "correct_option": 1
                    },
                    {
                        "id": 3,
                        "text": "Как лучше завершить разговор с клиентом?",
                        "options": [
                            "Спросить, есть ли еще вопросы, и попрощаться",
                            "Быстро сказать до свидания",
                            "Попросить оценить качество обслуживания",
                            "Пожелать хорошего дня"
                        ],
                        "correct_option": 0
                    }
                ],
                "is_active": True
            }
            
            test2 = {
                "title": "Тест по техническим знаниям",
                "description": "Тест для оценки технических знаний сотрудников",
                "questions": [
                    {
                        "id": 1,
                        "text": "Что такое API?",
                        "options": [
                            "Программа для работы с графикой",
                            "Интерфейс программирования приложений",
                            "Алгоритм обработки информации",
                            "Автоматизированная система контроля"
                        ],
                        "correct_option": 1
                    },
                    {
                        "id": 2,
                        "text": "Что означает HTTP?",
                        "options": [
                            "Hypertext Transfer Protocol",
                            "High Transfer Text Protocol",
                            "Hypertext Text Processing",
                            "Home Tool Transfer Protocol"
                        ],
                        "correct_option": 0
                    }
                ],
                "is_active": True
            }
            
            cursor.execute('''
            INSERT INTO multiple_choice_tests (title, description, questions, created_at, is_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (test1["title"], test1["description"], json.dumps(test1["questions"]), datetime.now(), test1["is_active"]))
            
            cursor.execute('''
            INSERT INTO multiple_choice_tests (title, description, questions, created_at, is_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (test2["title"], test2["description"], json.dumps(test2["questions"]), datetime.now(), test2["is_active"]))
            
            logger.info("Примеры тестов созданы")
        else:
            logger.info("Примеры тестов уже существуют")
            
        # Проверяем, существуют ли чаты в таблице communications
        cursor.execute("SELECT COUNT(*) FROM communications WHERE details IS NOT NULL AND details != '{}'")
        if cursor.fetchone()[0] == 0:
            logger.info("Создаем примеры чатов...")
            
            # Получаем ID клиента
            cursor.execute("SELECT id FROM clients WHERE email = 'client@example.com'")
            client_id = cursor.fetchone()[0]
            
            # Получаем ID оператора
            cursor.execute("SELECT id FROM employees WHERE name = 'support'")
            employee_id = cursor.fetchone()[0]
            
            # Создаем примеры чатов
            now = datetime.now()
            
            # Чат 1: Завершенный успешный чат
            chat1_time = now - timedelta(days=2)
            chat1_messages = {
                "messages": [
                    {
                        "sender": "client",
                        "message": "Здравствуйте! У меня возникла проблема с оплатой.",
                        "timestamp": (chat1_time).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Добрый день! Я Ваш оператор поддержки. Расскажите подробнее о проблеме с оплатой.",
                        "timestamp": (chat1_time + timedelta(minutes=1)).isoformat()
                    },
                    {
                        "sender": "client",
                        "message": "Я пытаюсь оплатить заказ, но система выдает ошибку 'Недопустимая карта'.",
                        "timestamp": (chat1_time + timedelta(minutes=2)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Давайте проверим данные Вашей карты. Скажите, Вы правильно ввели номер карты, срок действия и CVV-код?",
                        "timestamp": (chat1_time + timedelta(minutes=3)).isoformat()
                    },
                    {
                        "sender": "client",
                        "message": "Да, я проверил несколько раз. Все данные введены верно.",
                        "timestamp": (chat1_time + timedelta(minutes=4)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Понял, давайте попробуем другой способ оплаты. Вы можете воспользоваться электронным кошельком или оплатить через мобильное приложение банка.",
                        "timestamp": (chat1_time + timedelta(minutes=5)).isoformat()
                    },
                    {
                        "sender": "client",
                        "message": "Хорошо, я попробую оплатить через приложение банка. Спасибо за помощь!",
                        "timestamp": (chat1_time + timedelta(minutes=6)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Пожалуйста! Если у Вас возникнут еще вопросы, я всегда готов помочь. Хорошего дня!",
                        "timestamp": (chat1_time + timedelta(minutes=7)).isoformat()
                    }
                ]
            }
            
            # Чат 2: Текущий активный чат
            chat2_time = now - timedelta(minutes=20)
            chat2_messages = {
                "messages": [
                    {
                        "sender": "client",
                        "message": "Здравствуйте, подскажите, как мне отследить мой заказ?",
                        "timestamp": (chat2_time).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Здравствуйте! Чтобы отследить заказ, мне нужен его номер. Можете сообщить номер заказа?",
                        "timestamp": (chat2_time + timedelta(minutes=1)).isoformat()
                    },
                    {
                        "sender": "client",
                        "message": "Да, конечно. Номер заказа: ORD-12345678",
                        "timestamp": (chat2_time + timedelta(minutes=2)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Спасибо! Я проверю информацию по Вашему заказу. Подождите, пожалуйста, несколько минут.",
                        "timestamp": (chat2_time + timedelta(minutes=3)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Спасибо за ожидание! Ваш заказ был отправлен вчера и сейчас находится в пути. Предполагаемая дата доставки - завтра до 18:00.",
                        "timestamp": (chat2_time + timedelta(minutes=5)).isoformat()
                    }
                ]
            }
            
            # Чат 3: Чат с проблемным клиентом
            chat3_time = now - timedelta(days=1)
            chat3_messages = {
                "messages": [
                    {
                        "sender": "client",
                        "message": "Я уже третий раз обращаюсь по поводу бракованного товара! Когда вы решите мою проблему?",
                        "timestamp": (chat3_time).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Здравствуйте! Приносим извинения за доставленные неудобства. Я проверю историю Вашего обращения и постараюсь как можно быстрее решить проблему.",
                        "timestamp": (chat3_time + timedelta(minutes=1)).isoformat()
                    },
                    {
                        "sender": "client",
                        "message": "Каждый раз одно и то же! Проверяете, а результата нет! Я требую возврата денег!",
                        "timestamp": (chat3_time + timedelta(minutes=2)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Я понимаю Ваше возмущение. В данной ситуации возврат средств - это обоснованное требование. Я инициирую процедуру возврата прямо сейчас.",
                        "timestamp": (chat3_time + timedelta(minutes=3)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Я оформил заявку на возврат денежных средств. Средства должны поступить на Ваш счет в течение 3-5 рабочих дней. Также я добавил к Вашему аккаунту бонус на следующую покупку в качестве компенсации за неудобства.",
                        "timestamp": (chat3_time + timedelta(minutes=5)).isoformat()
                    },
                    {
                        "sender": "client",
                        "message": "Хорошо, буду ждать возврата. Надеюсь, в этот раз всё будет сделано правильно.",
                        "timestamp": (chat3_time + timedelta(minutes=6)).isoformat()
                    },
                    {
                        "sender": "employee",
                        "message": "Обязательно проконтролирую выполнение возврата лично. Если у Вас возникнут вопросы, Вы можете обратиться ко мне напрямую.",
                        "timestamp": (chat3_time + timedelta(minutes=7)).isoformat()
                    }
                ]
            }
            
            # Вставляем чаты в базу данных
            cursor.execute('''
            INSERT INTO communications (client_id, employee_id, timestamp, duration, success_rate, call_type, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, employee_id, chat1_time, 420, 0.9, "incoming", "completed", json.dumps(chat1_messages)))
            
            cursor.execute('''
            INSERT INTO communications (client_id, employee_id, timestamp, duration, success_rate, call_type, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, employee_id, chat2_time, None, None, "incoming", "active", json.dumps(chat2_messages)))
            
            cursor.execute('''
            INSERT INTO communications (client_id, employee_id, timestamp, duration, success_rate, call_type, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, employee_id, chat3_time, 420, 0.6, "incoming", "completed", json.dumps(chat3_messages)))
            
            logger.info("Примеры чатов созданы")
        else:
            logger.info("Примеры чатов уже существуют")
        
        conn.commit()
        logger.info("Все таблицы успешно созданы и заполнены тестовыми данными")
        
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_db() 