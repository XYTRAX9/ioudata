from app.database import SessionLocal, engine
from app import models

def clear_database():
    db = SessionLocal()
    try:
        # Удаляем все данные из таблиц
        db.query(models.Communication).delete()
        db.query(models.TestResult).delete()
        db.query(models.MultipleChoiceTest).delete()
        db.query(models.Client).delete()
        db.query(models.Employee).delete()
        db.commit()
        print("База данных успешно очищена!")
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_database() 