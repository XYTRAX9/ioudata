import sqlite3

db = sqlite3.connect('test.db')

c = db.cursor()

# Создание таблиц

c.execute("""CREATE TABLE users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    role             TEXT NOT NULL CHECK (role IN ('operator','admin')),
    current_status   TEXT NOT NULL DEFAULT 'free'
)""")

c.execute("""CREATE TABLE stress_results (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type         TEXT NOT NULL CHECK (type IN ('audio','video')),
    score        INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    file_path    TEXT,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)""")

c.execute("""CREATE TABLE call_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    client_id      TEXT NOT NULL, 
    result         TEXT NOT NULL CHECK (result IN ('success','failure')),
    started_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at    DATETIME
)""")

#Добавление значений в табл

# c.execute("INSERT INTO priority VALUES('Низкий')")

# c.execute("INSERT INTO priority VALUES('Средний')")

# c.execute("INSERT INTO priority VALUES('Высокий')")

# c.execute("INSERT INTO status VALUES('Открытый')")

# c.execute("INSERT INTO status VALUES('Закрытый')")

# c.execute("INSERT INTO roles VALUES('Пользователь')")

# c.execute("INSERT INTO roles VALUES('Исполнитель')")

# c.execute("INSERT INTO roles VALUES('Админ')")





# Удаление данных

# c.execute("DELETE FROM articles rowid > 2")

# Обновление данных

# c.execute("UPDATE articles SET author 'Admin' WHERE title = 'Google is cool!' ")





# Выборка

# c.execute("SELECT * FROM articles")
# c.execute("SELECT rowid, * FROM articles WHERE rowid = 2")
# c.execute("SELECT rowid, * FROM articles WHERE title <> 'Google is cool!'")
#c.execute("SELECT rowid, * FROM articles WHERE rowid < 5 ORDER BY rowid DESC")

# <> = не равно

#items = c.fetchall()

# print(c.fetchall())
# print(c.fetchmany(1))
# print(c.fetchone()[1])




# Вывод всех значений

#for el in items:
#    print(el[1] + "\n" + el[4])

db.commit()


db.close()
