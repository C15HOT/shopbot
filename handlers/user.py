from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

from config import WELCOME_MESSAGE, ORDER_MESSAGE, SELLER_CONTACT, ADMIN_ID
from keyboards.inline import get_categories_keyboard, get_products_keyboard, get_product_detail_keyboard
from utils.database import get_categories, get_products_by_category, get_product

router = Router()

def get_main_menu_keyboard(is_admin: bool = False):
    """Create main menu keyboard"""
    keyboard_buttons = [[KeyboardButton(text="🛍️ Каталог товаров")]]
    
    if is_admin:
        keyboard_buttons.append([KeyboardButton(text="👑 Админ панель")])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

@router.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    categories_kb = await get_categories_keyboard()
    is_admin = message.from_user.id == ADMIN_ID
    main_menu = get_main_menu_keyboard(is_admin)
    
    if categories_kb:
        await message.answer(WELCOME_MESSAGE, reply_markup=categories_kb)
        await message.answer("Используйте меню внизу для быстрого доступа:", reply_markup=main_menu)
    else:
        await message.answer("❌ Категории товаров пока не добавлены.", reply_markup=main_menu)

@router.message(F.text == "🛍️ Каталог товаров")
async def show_catalog(message: Message):
    """Show catalog of products"""
    categories_kb = await get_categories_keyboard()
    if categories_kb:
        await message.answer(WELCOME_MESSAGE, reply_markup=categories_kb)
    else:
        await message.answer("❌ Категории товаров пока не добавлены.")

@router.message(F.text == "👑 Админ панель")
async def admin_panel_shortcut(message: Message):
    """Shortcut to admin panel"""
    # Check if user is admin
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ панели.")
        return
    
    from handlers.admin import admin_panel
    await admin_panel(message)

@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    """Show products in selected category"""
    category_id = int(callback.data.split("_")[1])
    
    products_kb = await get_products_keyboard(category_id)
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная категория")
    
    if products_kb:
        await callback.message.edit_text(
            f"🛍️ Товары в категории <b>{category_name}</b>:\n\nВыберите товар:",
            reply_markup=products_kb,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"❌ В категории <b>{category_name}</b> пока нет товаров.",
            reply_markup=await get_categories_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery):
    """Show product details"""
    product_id = int(callback.data.split("_")[1])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    product_text = f"""
🛍️ <b>{product['name']}</b>

📝 {product['description']}

💰 Цена: <b>{product['price']} руб.</b>
"""
    
    keyboard = get_product_detail_keyboard(product_id, product['category_id'])
    await callback.message.edit_text(product_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("order_"))
async def make_order(callback: CallbackQuery):
    """Show seller contact for ordering"""
    product_id = int(callback.data.split("_")[1])
    product = await get_product(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    order_text = ORDER_MESSAGE.format(contact=SELLER_CONTACT)
    order_text += f"\n\n🛍️ Товар: <b>{product['name']}</b>"
    
    await callback.message.answer(order_text, parse_mode="HTML")
    await callback.answer("✅ Контакт продавца отправлен!")

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    """Return to categories menu"""
    categories_kb = await get_categories_keyboard()
    if categories_kb:
        await callback.message.edit_text(WELCOME_MESSAGE, reply_markup=categories_kb)
    else:
        await callback.message.edit_text("❌ Категории товаров пока не добавлены.")
    await callback.answer()

@router.callback_query(F.data.startswith("back_to_category_"))
async def back_to_category(callback: CallbackQuery):
    """Return to category products"""
    category_id = int(callback.data.split("_")[3])
    
    products_kb = await get_products_keyboard(category_id)
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная категория")
    
    if products_kb:
        await callback.message.edit_text(
            f"🛍️ Товары в категории <b>{category_name}</b>:\n\nВыберите товар:",
            reply_markup=products_kb,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"❌ В категории <b>{category_name}</b> пока нет товаров.",
            reply_markup=await get_categories_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()
