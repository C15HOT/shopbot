from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold, hcode

from config import WELCOME_MESSAGE, ORDER_MESSAGE, SELLER_CONTACT
from keyboards.inline import get_categories_keyboard, get_products_keyboard, get_product_detail_keyboard
from utils.database import get_categories, get_products_by_category, get_product

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Handle /start command"""
    categories_kb = await get_categories_keyboard()
    if categories_kb:
        await message.answer(WELCOME_MESSAGE, reply_markup=categories_kb)
    else:
        await message.answer("❌ Категории товаров пока не добавлены.")

@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    """Show products in selected category"""
    category_id = int(callback.data.split("_")[1])
    
    products_kb = await get_products_keyboard(category_id)
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная категория")
    
    if products_kb:
        await callback.message.edit_text(
            f"🛍️ Товары в категории {hbold(category_name)}:\n\nВыберите товар:",
            reply_markup=products_kb
        )
    else:
        await callback.message.edit_text(
            f"❌ В категории {hbold(category_name)} пока нет товаров.",
            reply_markup=await get_categories_keyboard()
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
🛍️ {hbold(product['name'])}

📝 {product['description']}

💰 Цена: {hbold(str(product['price']) + ' руб.')}
"""
    
    keyboard = get_product_detail_keyboard(product_id, product['category_id'])
    await callback.message.edit_text(product_text, reply_markup=keyboard)
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
    order_text += f"\n\n🛍️ Товар: {hbold(product['name'])}"
    
    await callback.message.answer(order_text)
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
            f"🛍️ Товары в категории {hbold(category_name)}:\n\nВыберите товар:",
            reply_markup=products_kb
        )
    else:
        await callback.message.edit_text(
            f"❌ В категории {hbold(category_name)} пока нет товаров.",
            reply_markup=await get_categories_keyboard()
        )
    
    await callback.answer()
