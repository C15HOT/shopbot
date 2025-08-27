from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import get_categories, get_products_by_category

async def get_admin_category_products_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for managing products in specific category"""
    categories = await get_categories()
    products = await get_products_by_category(category_id)
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная категория")
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"➕ Добавить товар в {category_name}",
                callback_data=f"add_product_{category_id}"
            )
        ]
    ]
    
    if products:
        for product in products:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📦 {product['name']} - {product['price']} руб.",
                    callback_data=f"view_product_{product['id']}"
                )
            ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="◀️ Назад к категориям",
            callback_data="admin_products"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_product_admin_keyboard(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for product administration"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✏️ Название",
                callback_data=f"edit_product_name_{product_id}"
            ),
            InlineKeyboardButton(
                text="💰 Цена",
                callback_data=f"edit_product_price_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Описание",
                callback_data=f"edit_product_description_{product_id}"
            )
        ],
        [ InlineKeyboardButton(text="📸 Изображение", callback_data=f"edit_product_image_{product_id}"),
        InlineKeyboardButton(text="🗑️ Удалить фото", callback_data=f"delete_product_image_{product_id}")],
        [
            InlineKeyboardButton(
                text="🗑️ Удалить товар",
                callback_data=f"delete_product_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад к товарам",
                callback_data=f"admin_category_products_{category_id}"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)