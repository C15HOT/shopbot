from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import get_categories, get_products, get_products_by_category

async def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with categories"""
    categories = await get_categories()
    
    if not categories:
        return None
    
    keyboard = []
    for category in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📂 {category['name']}",
                callback_data=f"category_{category['id']}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_products_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Create keyboard with products from category"""
    products = await get_products_by_category(category_id)
    
    if not products:
        return None
    
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🛍️ {product['name']} - {product['price']} руб.",
                callback_data=f"product_{product['id']}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton(
            text="◀️ Назад к категориям",
            callback_data="back_to_categories"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_product_detail_keyboard(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for product details"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 Сделать заказ",
                callback_data=f"order_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад к товарам",
                callback_data=f"back_to_category_{category_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📂 К категориям",
                callback_data="back_to_categories"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Create admin panel keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📂 Управление категориями",
                callback_data="admin_categories"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛍️ Управление товарами",
                callback_data="admin_products"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_admin_categories_keyboard() -> InlineKeyboardMarkup:
    """Create admin categories management keyboard"""
    categories = await get_categories()
    
    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Добавить категорию",
                callback_data="add_category"
            )
        ]
    ]
    
    if categories:
        for category in categories:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"✏️ {category['name']}",
                    callback_data=f"edit_category_{category['id']}"
                ),
                InlineKeyboardButton(
                    text="🗑️",
                    callback_data=f"delete_category_{category['id']}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="◀️ Назад в панель",
            callback_data="back_to_admin"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_admin_products_keyboard() -> InlineKeyboardMarkup:
    """Create admin products management keyboard"""
    categories = await get_categories()
    products = await get_products()
    
    keyboard = []
    
    # Add product buttons by category
    if categories:
        keyboard.append([
            InlineKeyboardButton(
                text="➕ Добавить товар",
                callback_data="admin_add_product_select"
            )
        ])
        
        for category in categories:
            category_products = [p for p in products if p['category_id'] == category['id']]
            if category_products:
                # Add category header
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"📂 {category['name']}",
                        callback_data=f"add_product_{category['id']}"
                    )
                ])
                
                # Add products in this category
                for product in category_products:
                    keyboard.append([
                        InlineKeyboardButton(
                            text=f"✏️ {product['name']} - {product['price']} руб.",
                            callback_data=f"edit_product_{product['id']}"
                        ),
                        InlineKeyboardButton(
                            text="🗑️",
                            callback_data=f"delete_product_{product['id']}"
                        )
                    ])
            else:
                # Category with no products - just add button
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"➕ Добавить в {category['name']}",
                        callback_data=f"add_product_{category['id']}"
                    )
                ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="◀️ Назад в панель",
            callback_data="back_to_admin"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
