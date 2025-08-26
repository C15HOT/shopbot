"""
Database initialization script
Run this file to create database tables
"""
import asyncio
from utils.database import init_database

async def main():
    """Initialize database tables"""
    print("Инициализация базы данных...")
    try:
        await init_database()
        print("✅ База данных успешно инициализирована!")
        print("Таблицы categories и products созданы.")
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")

if __name__ == "__main__":
    asyncio.run(main())