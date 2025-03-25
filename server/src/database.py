# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Получаем параметры подключения из переменных окружения или используем значения по умолчанию
DATABASE_USER = os.environ.get("POSTGRES_USER", "postgres")
DATABASE_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
DATABASE_HOST = os.environ.get("POSTGRES_HOST", "db")  # имя сервиса базы данных в docker-compose
DATABASE_PORT = os.environ.get("POSTGRES_PORT", "5432")
DATABASE_NAME = os.environ.get("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Создание движка базы данных:
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий:
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для моделей:
Base = declarative_base()

# Создаем все таблицы, если их еще нет
Base.metadata.create_all(bind=engine)
