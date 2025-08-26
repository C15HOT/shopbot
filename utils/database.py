import json
import os
import asyncio
from typing import List, Dict, Optional

from config import CATEGORIES_FILE, PRODUCTS_FILE

# In-memory storage
categories_data = []
products_data = []
next_category_id = 1
next_product_id = 1

async def init_database():
    """Initialize database and load existing data"""
    global categories_data, products_data, next_category_id, next_product_id
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Load categories
    if os.path.exists(CATEGORIES_FILE):
        try:
            with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                categories_data = data.get('categories', [])
                next_category_id = data.get('next_id', 1)
        except (json.JSONDecodeError, FileNotFoundError):
            categories_data = []
            next_category_id = 1
    else:
        await save_categories()
    
    # Load products
    if os.path.exists(PRODUCTS_FILE):
        try:
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                products_data = data.get('products', [])
                next_product_id = data.get('next_id', 1)
        except (json.JSONDecodeError, FileNotFoundError):
            products_data = []
            next_product_id = 1
    else:
        await save_products()

async def save_categories():
    """Save categories to file"""
    data = {
        'categories': categories_data,
        'next_id': next_category_id
    }
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def save_products():
    """Save products to file"""
    data = {
        'products': products_data,
        'next_id': next_product_id
    }
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Category operations
async def get_categories() -> List[Dict]:
    """Get all categories"""
    return categories_data.copy()

async def add_category(name: str) -> int:
    """Add new category"""
    global next_category_id
    
    category = {
        'id': next_category_id,
        'name': name
    }
    
    categories_data.append(category)
    category_id = next_category_id
    next_category_id += 1
    
    await save_categories()
    return category_id

async def delete_category(category_id: int) -> bool:
    """Delete category and all its products"""
    global categories_data, products_data
    
    # Remove category
    categories_data = [cat for cat in categories_data if cat['id'] != category_id]
    
    # Remove all products in this category
    products_data = [prod for prod in products_data if prod['category_id'] != category_id]
    
    await save_categories()
    await save_products()
    return True

async def update_category(category_id: int, new_name: str) -> bool:
    """Update category name"""
    for category in categories_data:
        if category['id'] == category_id:
            category['name'] = new_name
            await save_categories()
            return True
    return False

# Product operations
async def get_products() -> List[Dict]:
    """Get all products"""
    return products_data.copy()

async def get_products_by_category(category_id: int) -> List[Dict]:
    """Get products by category"""
    return [prod for prod in products_data if prod['category_id'] == category_id]

async def get_product(product_id: int) -> Optional[Dict]:
    """Get product by ID"""
    return next((prod for prod in products_data if prod['id'] == product_id), None)

async def add_product(name: str, description: str, price: float, category_id: int) -> int:
    """Add new product"""
    global next_product_id
    
    product = {
        'id': next_product_id,
        'name': name,
        'description': description,
        'price': price,
        'category_id': category_id
    }
    
    products_data.append(product)
    product_id = next_product_id
    next_product_id += 1
    
    await save_products()
    return product_id

async def delete_product(product_id: int) -> bool:
    """Delete product"""
    global products_data
    
    initial_length = len(products_data)
    products_data = [prod for prod in products_data if prod['id'] != product_id]
    
    if len(products_data) < initial_length:
        await save_products()
        return True
    return False

async def update_product(product_id: int, name: str, description: str, price: float) -> bool:
    """Update product"""
    for product in products_data:
        if product['id'] == product_id:
            product['name'] = name
            product['description'] = description
            product['price'] = price
            await save_products()
            return True
    return False
