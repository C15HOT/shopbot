from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold

from config import ADMIN_ID, ADMIN_WELCOME_MESSAGE
from keyboards.inline import get_admin_keyboard, get_admin_categories_keyboard, get_admin_products_keyboard
from keyboards.admin_extended import get_admin_category_products_keyboard, get_product_admin_keyboard
from utils.database import (
    add_category, delete_category, update_category, get_categories,
    add_product, delete_product, update_product, get_products, get_product
)

router = Router()

class AdminStates(StatesGroup):
    waiting_category_name = State()
    waiting_new_category_name = State()
    waiting_product_name = State()
    waiting_product_description = State()
    waiting_product_price = State()
    waiting_new_product_name = State()
    waiting_new_product_description = State()
    waiting_new_product_price = State()
    waiting_product_field_name = State()
    waiting_product_field_description = State()
    waiting_product_field_price = State()

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Show admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к панели администратора.")
        return
    
    admin_kb = get_admin_keyboard()
    await message.answer(ADMIN_WELCOME_MESSAGE, reply_markup=admin_kb)

@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    """Show categories management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    categories_kb = await get_admin_categories_keyboard()
    await callback.message.edit_text("📂 Управление категориями:", reply_markup=categories_kb)
    await callback.answer()

@router.callback_query(F.data == "admin_products")
async def admin_products(callback: CallbackQuery):
    """Show products management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    products_kb = await get_admin_products_keyboard()
    await callback.message.edit_text("🛍️ Управление товарами:", reply_markup=products_kb)
    await callback.answer()

@router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    """Start adding new category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    await callback.message.answer("📝 Введите название новой категории:")
    await state.set_state(AdminStates.waiting_category_name)
    await callback.answer()

@router.message(AdminStates.waiting_category_name)
async def add_category_finish(message: Message, state: FSMContext):
    """Finish adding new category"""
    category_name = message.text.strip()
    
    if len(category_name) < 1:
        await message.answer("❌ Название категории не может быть пустым!")
        return
    
    category_id = await add_category(category_name)
    await message.answer(f"✅ Категория <b>{category_name}</b> добавлена!", parse_mode="HTML")
    
    # Show categories management menu again
    categories_kb = await get_admin_categories_keyboard()
    await message.answer("📂 Управление категориями:", reply_markup=categories_kb)
    await state.clear()

@router.callback_query(F.data.startswith("delete_category_"))
async def delete_category_handler(callback: CallbackQuery):
    """Delete category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[2])
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), None)
    
    if category_name:
        await delete_category(category_id)
        await callback.answer(f"✅ Категория {category_name} удалена!")
        
        # Update the keyboard
        categories_kb = await get_admin_categories_keyboard()
        await callback.message.edit_reply_markup(reply_markup=categories_kb)
    else:
        await callback.answer("❌ Категория не найдена!", show_alert=True)

@router.callback_query(F.data.startswith("edit_category_"))
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    """Start editing category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=category_id)
    
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), None)
    
    if category_name:
        await callback.message.answer(f"📝 Текущее название: <b>{category_name}</b>\n\nВведите новое название категории:", parse_mode="HTML")
        await state.set_state(AdminStates.waiting_new_category_name)
    else:
        await callback.answer("❌ Категория не найдена!", show_alert=True)
    
    await callback.answer()

@router.message(AdminStates.waiting_new_category_name)
async def edit_category_finish(message: Message, state: FSMContext):
    """Finish editing category"""
    new_name = message.text.strip()
    
    if len(new_name) < 1:
        await message.answer("❌ Название категории не может быть пустым!")
        return
    
    data = await state.get_data()
    category_id = data["category_id"]
    
    await update_category(category_id, new_name)
    await message.answer(f"✅ Название категории изменено на <b>{new_name}</b>!", parse_mode="HTML")
    
    # Show categories management menu again
    categories_kb = await get_admin_categories_keyboard()
    await message.answer("📂 Управление категориями:", reply_markup=categories_kb)
    await state.clear()

@router.callback_query(F.data.startswith("add_product_"))
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    """Start adding new product"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=category_id)
    
    await callback.message.answer("📝 Введите название товара:")
    await state.set_state(AdminStates.waiting_product_name)
    await callback.answer()

@router.message(AdminStates.waiting_product_name)
async def add_product_description(message: Message, state: FSMContext):
    """Get product description"""
    product_name = message.text.strip()
    
    if len(product_name) < 1:
        await message.answer("❌ Название товара не может быть пустым!")
        return
    
    await state.update_data(product_name=product_name)
    await message.answer("📝 Введите описание товара:")
    await state.set_state(AdminStates.waiting_product_description)

@router.message(AdminStates.waiting_product_description)
async def add_product_price(message: Message, state: FSMContext):
    """Get product price"""
    product_description = message.text.strip()
    
    if len(product_description) < 1:
        await message.answer("❌ Описание товара не может быть пустым!")
        return
    
    await state.update_data(product_description=product_description)
    await message.answer("💰 Введите цену товара (только число):")
    await state.set_state(AdminStates.waiting_product_price)

@router.message(AdminStates.waiting_product_price)
async def add_product_finish(message: Message, state: FSMContext):
    """Finish adding new product"""
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError("Price must be positive")
    except ValueError:
        await message.answer("❌ Цена должна быть положительным числом!")
        return
    
    data = await state.get_data()
    
    product_id = await add_product(
        data["product_name"],
        data["product_description"],
        price,
        data["category_id"]
    )
    
    await message.answer(f"✅ Товар <b>{data['product_name']}</b> добавлен!", parse_mode="HTML")
    
    # Show products management menu again
    products_kb = await get_admin_products_keyboard()
    await message.answer("🛍️ Управление товарами:", reply_markup=products_kb)
    await state.clear()

@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product_handler(callback: CallbackQuery):
    """Delete product"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[2])
    product = await get_product(product_id)
    
    if product:
        await delete_product(product_id)
        await callback.answer(f"✅ Товар {product['name']} удален!")
        
        # Update the keyboard
        products_kb = await get_admin_products_keyboard()
        await callback.message.edit_reply_markup(reply_markup=products_kb)
    else:
        await callback.answer("❌ Товар не найден!", show_alert=True)

@router.callback_query(F.data.regex(r"^edit_product_\d+$"))
async def edit_product_start_old(callback: CallbackQuery, state: FSMContext):
    """Start editing product (old handler for backward compatibility)"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[2])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await state.update_data(product_id=product_id)
    await callback.message.answer(f"📝 Текущее название: <b>{product['name']}</b>\n\nВведите новое название товара:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_new_product_name)
    await callback.answer()

@router.message(AdminStates.waiting_new_product_name)
async def edit_product_description(message: Message, state: FSMContext):
    """Edit product description"""
    product_name = message.text.strip()
    
    if len(product_name) < 1:
        await message.answer("❌ Название товара не может быть пустым!")
        return
    
    await state.update_data(new_product_name=product_name)
    
    data = await state.get_data()
    product = await get_product(data["product_id"])
    
    await message.answer(f"📝 Текущее описание: <b>{product['description']}</b>\n\nВведите новое описание товара:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_new_product_description)

@router.message(AdminStates.waiting_new_product_description)
async def edit_product_price_input(message: Message, state: FSMContext):
    """Edit product price"""
    product_description = message.text.strip()
    
    if len(product_description) < 1:
        await message.answer("❌ Описание товара не может быть пустым!")
        return
    
    await state.update_data(new_product_description=product_description)
    
    data = await state.get_data()
    product = await get_product(data["product_id"])
    
    await message.answer(f"💰 Текущая цена: <b>{product['price']} руб.</b>\n\nВведите новую цену товара (только число):", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_new_product_price)

@router.message(AdminStates.waiting_new_product_price)
async def edit_product_finish(message: Message, state: FSMContext):
    """Finish editing product"""
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError("Price must be positive")
    except ValueError:
        await message.answer("❌ Цена должна быть положительным числом!")
        return
    
    data = await state.get_data()
    
    await update_product(
        data["product_id"],
        data["new_product_name"],
        data["new_product_description"],
        price
    )
    
    await message.answer(f"✅ Товар <b>{data['new_product_name']}</b> обновлен!", parse_mode="HTML")
    
    # Show products management menu again
    products_kb = await get_admin_products_keyboard()
    await message.answer("🛍️ Управление товарами:", reply_markup=products_kb)
    await state.clear()

@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    """Return to admin panel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    admin_kb = get_admin_keyboard()
    await callback.message.edit_text(ADMIN_WELCOME_MESSAGE, reply_markup=admin_kb)
    await callback.answer()

# New handlers for improved product management
@router.callback_query(F.data.startswith("admin_category_products_"))
async def admin_category_products(callback: CallbackQuery):
    """Show products in specific category for management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    category_id = int(callback.data.split("_")[3])
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная категория")
    
    products_kb = await get_admin_category_products_keyboard(category_id)
    await callback.message.edit_text(f"🛍️ Товары в категории <b>{category_name}</b>:", reply_markup=products_kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("view_product_"))
async def view_product_admin(callback: CallbackQuery):
    """Show product details for admin"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[2])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    product_text = f"""
📦 <b>{product['name']}</b>

📝 Описание: {product['description']}

💰 Цена: <b>{product['price']} руб.</b>

Выберите что хотите изменить:
"""
    
    keyboard = get_product_admin_keyboard(product_id, product['category_id'])
    await callback.message.edit_text(product_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("edit_product_name_"))
async def edit_product_name_start(callback: CallbackQuery, state: FSMContext):
    """Start editing product name"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[4])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, category_id=product['category_id'])
    await callback.message.answer(f"✏️ Текущее название: <b>{product['name']}</b>\n\nВведите новое название товара:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_product_field_name)
    await callback.answer()

@router.message(AdminStates.waiting_product_field_name)
async def edit_product_name_finish(message: Message, state: FSMContext):
    """Finish editing product name"""
    new_name = message.text.strip()
    
    if len(new_name) < 1:
        await message.answer("❌ Название товара не может быть пустым!")
        return
    
    data = await state.get_data()
    product = await get_product(data["product_id"])
    
    await update_product(data["product_id"], new_name, product['description'], product['price'])
    await message.answer(f"✅ Название товара изменено на: <b>{new_name}</b>", parse_mode="HTML")
    
    # Show category products again
    products_kb = await get_admin_category_products_keyboard(data["category_id"])
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == data["category_id"]), "Категория")
    await message.answer(f"🛍️ Товары в категории <b>{category_name}</b>:", reply_markup=products_kb, parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data.startswith("edit_product_price_"))
async def edit_product_price_start(callback: CallbackQuery, state: FSMContext):
    """Start editing product price"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[4])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, category_id=product['category_id'])
    await callback.message.answer(f"💰 Текущая цена: <b>{product['price']} руб.</b>\n\nВведите новую цену товара (только число):", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_product_field_price)
    await callback.answer()

@router.message(AdminStates.waiting_product_field_price)
async def edit_product_price_finish(message: Message, state: FSMContext):
    """Finish editing product price"""
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError("Price must be positive")
    except ValueError:
        await message.answer("❌ Цена должна быть положительным числом!")
        return
    
    data = await state.get_data()
    product = await get_product(data["product_id"])
    
    await update_product(data["product_id"], product['name'], product['description'], price)
    await message.answer(f"✅ Цена товара изменена на: <b>{price} руб.</b>", parse_mode="HTML")
    
    # Show category products again
    products_kb = await get_admin_category_products_keyboard(data["category_id"])
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == data["category_id"]), "Категория")
    await message.answer(f"🛍️ Товары в категории <b>{category_name}</b>:", reply_markup=products_kb, parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data.startswith("edit_product_description_"))
async def edit_product_description_start(callback: CallbackQuery, state: FSMContext):
    """Start editing product description"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен!", show_alert=True)
        return
    
    product_id = int(callback.data.split("_")[4])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, category_id=product['category_id'])
    await callback.message.answer(f"📝 Текущее описание: <b>{product['description']}</b>\n\nВведите новое описание товара:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_product_field_description)
    await callback.answer()

@router.message(AdminStates.waiting_product_field_description)
async def edit_product_description_finish(message: Message, state: FSMContext):
    """Finish editing product description"""
    new_description = message.text.strip()
    
    if len(new_description) < 1:
        await message.answer("❌ Описание товара не может быть пустым!")
        return
    
    data = await state.get_data()
    product = await get_product(data["product_id"])
    
    await update_product(data["product_id"], product['name'], new_description, product['price'])
    await message.answer(f"✅ Описание товара изменено!", parse_mode="HTML")
    
    # Show category products again
    products_kb = await get_admin_category_products_keyboard(data["category_id"])
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == data["category_id"]), "Категория")
    await message.answer(f"🛍️ Товары в категории <b>{category_name}</b>:", reply_markup=products_kb, parse_mode="HTML")
    await state.clear()
