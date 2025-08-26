import os
import asyncio
import asyncpg
from typing import List, Dict, Optional

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

async def get_connection():
    """Get database connection"""
    return await asyncpg.connect(DATABASE_URL)

async def init_database():
    """Initialize database and create tables"""
    conn = await get_connection()
    try:
        # Create categories table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')
        
        # Create products table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
            )
        ''')
        
    finally:
        await conn.close()

# Category operations
async def get_categories() -> List[Dict]:
    """Get all categories"""
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT id, name FROM categories ORDER BY id")
        return [{"id": row["id"], "name": row["name"]} for row in rows]
    finally:
        await conn.close()

async def add_category(name: str) -> int:
    """Add new category"""
    conn = await get_connection()
    try:
        row = await conn.fetchrow("INSERT INTO categories (name) VALUES ($1) RETURNING id", name)
        return row["id"]
    finally:
        await conn.close()

async def delete_category(category_id: int) -> bool:
    """Delete category and all its products"""
    conn = await get_connection()
    try:
        result = await conn.execute("DELETE FROM categories WHERE id = $1", category_id)
        return result.split()[-1] != "0"  # Check if rows were affected
    finally:
        await conn.close()

async def update_category(category_id: int, new_name: str) -> bool:
    """Update category name"""
    conn = await get_connection()
    try:
        result = await conn.execute("UPDATE categories SET name = $1 WHERE id = $2", new_name, category_id)
        return result.split()[-1] != "0"  # Check if rows were affected
    finally:
        await conn.close()

# Product operations
async def get_products() -> List[Dict]:
    """Get all products"""
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT id, name, description, price, category_id FROM products ORDER BY id")
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "price": float(row["price"]),
                "category_id": row["category_id"]
            }
            for row in rows
        ]
    finally:
        await conn.close()

async def get_products_by_category(category_id: int) -> List[Dict]:
    """Get products by category"""
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            "SELECT id, name, description, price, category_id FROM products WHERE category_id = $1 ORDER BY id",
            category_id
        )
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "price": float(row["price"]),
                "category_id": row["category_id"]
            }
            for row in rows
        ]
    finally:
        await conn.close()

async def get_product(product_id: int) -> Optional[Dict]:
    """Get product by ID"""
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT id, name, description, price, category_id FROM products WHERE id = $1",
            product_id
        )
        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "price": float(row["price"]),
                "category_id": row["category_id"]
            }
        return None
    finally:
        await conn.close()

async def add_product(name: str, description: str, price: float, category_id: int) -> int:
    """Add new product"""
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "INSERT INTO products (name, description, price, category_id) VALUES ($1, $2, $3, $4) RETURNING id",
            name, description, price, category_id
        )
        return row["id"]
    finally:
        await conn.close()

async def delete_product(product_id: int) -> bool:
    """Delete product"""
    conn = await get_connection()
    try:
        result = await conn.execute("DELETE FROM products WHERE id = $1", product_id)
        return result.split()[-1] != "0"  # Check if rows were affected
    finally:
        await conn.close()

async def update_product(product_id: int, name: str, description: str, price: float) -> bool:
    """Update product"""
    conn = await get_connection()
    try:
        result = await conn.execute(
            "UPDATE products SET name = $1, description = $2, price = $3 WHERE id = $4",
            name, description, price, product_id
        )
        return result.split()[-1] != "0"  # Check if rows were affected
    finally:
        await conn.close()