import logging
import os
import sqlite3
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
            blacklisted_employees TEXT DEFAULT '[]'
        )
        ''')
        
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
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')
        
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
            INSERT INTO clients (name, phone, email, hashed_password)
            VALUES (?, ?, ?, ?)
            ''', ('Тестовый Клиент', '+7-999-999-9999', 'client@example.com', hashed_password))
            logger.info("Создан тестовый клиент")
        else:
            logger.info("Тестовый клиент уже существует")
        
        conn.commit()
        logger.info("Все таблицы успешно созданы")
        
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_db() 