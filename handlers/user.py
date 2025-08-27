import os
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

from config import WELCOME_MESSAGE, ORDER_MESSAGE, SELLER_CONTACT, ADMIN_ID, GROUP
from keyboards.inline import get_categories_keyboard, get_products_keyboard, get_product_detail_keyboard
from utils.database import get_categories, get_products_by_category, get_product

router = Router()

def get_main_menu_keyboard(is_admin: bool = False):
    """Create main menu keyboard"""
    keyboard_buttons = [[KeyboardButton(text="🛍️ Каталог товаров")]]
    keyboard_buttons.append([KeyboardButton(text="📣 Отзывы о нас")])

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

@router.message(F.text == "📣 Отзывы о нас")
async def return_link(message: Message):
    await message.answer(f"Посмотрите наши отзывы: {GROUP}")

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
    from aiogram.types import InputFile, FSInputFile
    
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
    
    # Show image if available
    if product.get('image_path') and os.path.exists(product['image_path']):
        try:
            photo = FSInputFile(product['image_path'])
            await callback.message.answer_photo(
                photo=photo, 
                caption=product_text, 
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            # If image fails to load, send text message
            await callback.message.answer(
                product_text + "\n\n🖼️ Ошибка при загрузке изображения.", 
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    else:
        # No image or image not found
        await callback.message.answer(
            product_text, 
            reply_markup=keyboard,
            parse_mode="HTML"
        )

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

    try:
        if categories_kb:
            if callback.message.photo:
                # Удаляем фото и отправляем новое приветствие с клавиатурой.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее фото-сообщение в back_to_categories: {delete_err}")
                    pass

                await callback.message.answer(
                    text=WELCOME_MESSAGE, # Предполагается, что WELCOME_MESSAGE - это ваша константа
                    reply_markup=categories_kb,
                    parse_mode="HTML" # Или как вы там форматируете WELCOME_MESSAGE
                )
            elif callback.message.text:
                # Редактируем текст, если он уже текстовый.
                await callback.message.edit_text(
                    text=WELCOME_MESSAGE,
                    reply_markup=categories_kb,
                    parse_mode="HTML"
                )
            else:
                # Если что-то другое, удаляем и отправляем новое.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее сообщение в back_to_categories: {delete_err}")
                    pass

                await callback.message.answer(
                    text=WELCOME_MESSAGE,
                    reply_markup=categories_kb,
                    parse_mode="HTML"
                )
        else:
            # Если категорий нет, и предыдущее сообщение было фото
            if callback.message.photo:
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее фото-сообщение в back_to_categories (no categories): {delete_err}")
                    pass

                await callback.message.answer(
                    text="❌ Категории товаров пока не добавлены.",
                    reply_markup=await get_categories_keyboard(), # На случай, если клавиатура пуста, но должна быть
                    parse_mode="HTML"
                )
            elif callback.message.text:
                # Редактируем текст.
                await callback.message.edit_text(
                    text="❌ Категории товаров пока не добавлены.",
                    reply_markup=await get_categories_keyboard(),
                    parse_mode="HTML"
                )
            else:
                # Удаляем и отправляем новое.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее сообщение в back_to_categories (no categories): {delete_err}")
                    pass

                await callback.message.answer(
                    text="❌ Категории товаров пока не добавлены.",
                    reply_markup=await get_categories_keyboard(),
                    parse_mode="HTML"
                )

        # await callback.answer() # Эта строка была дважды, убрал одну

    except Exception as e:
        print(f"Ошибка при обработке back_to_categories: {e}")
        await callback.answer("❌ Произошла ошибка при возврате к категориям!", show_alert=True)
    finally:
        # Важно вызывать callback.answer() в любом случае, чтобы убрать "loading"
        await callback.answer()


@router.callback_query(F.data.startswith("back_to_category_"))
async def back_to_category(callback: CallbackQuery):
    """Return to category products"""
    try:
        category_id = int(callback.data.split("_")[3])
    except (IndexError, ValueError):
        await callback.answer("❌ Неверный формат данных категории!", show_alert=True)
        return

    products_kb = await get_products_keyboard(category_id)
    categories = await get_categories()
    category_name = next((cat["name"] for cat in categories if cat["id"] == category_id), "Неизвестная категория")

    message_text = f"🛍️ Товары в категории <b>{category_name}</b>:\n\nВыберите товар:"
    no_products_text = f"❌ В категории <b>{category_name}</b> пока нет товаров."

    try:
        if products_kb: # Если товары есть и клавиатура создана
            if callback.message.photo:
                # Если предыдущее сообщение было с фото, удаляем его и отправляем текст.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее фото-сообщение в back_to_category: {delete_err}")
                    pass # Продолжаем, даже если удаление не удалось

                await callback.message.answer(
                    text=message_text,
                    reply_markup=products_kb,
                    parse_mode="HTML"
                )
            elif callback.message.text:
                # Если предыдущее сообщение было текстом, безопасно редактируем.
                await callback.message.edit_text(
                    text=message_text,
                    reply_markup=products_kb,
                    parse_mode="HTML"
                )
            else:
                # Если предыдущее сообщение было чем-то другим, удаляем и отправляем новое.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее сообщение в back_to_category: {delete_err}")
                    pass

                await callback.message.answer(
                    text=message_text,
                    reply_markup=products_kb,
                    parse_mode="HTML"
                )
        else: # Если товаров нет
            if callback.message.photo:
                # Удаляем фото и отправляем сообщение о пустой категории.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее фото-сообщение в back_to_category (no products): {delete_err}")
                    pass

                await callback.message.answer(
                    text=no_products_text,
                    reply_markup=await get_categories_keyboard(), # Нужна клавиатура для возврата к категориям
                    parse_mode="HTML"
                )
            elif callback.message.text:
                # Редактируем текст, если он уже текстовый.
                await callback.message.edit_text(
                    text=no_products_text,
                    reply_markup=await get_categories_keyboard(),
                    parse_mode="HTML"
                )
            else:
                # Если что-то другое, удаляем и отправляем новое.
                try:
                    await callback.message.delete()
                except Exception as delete_err:
                    print(f"Не удалось удалить предыдущее сообщение в back_to_category (no products): {delete_err}")
                    pass

                await callback.message.answer(
                    text=no_products_text,
                    reply_markup=await get_categories_keyboard(),
                    parse_mode="HTML"
                )

        await callback.answer()

    except Exception as e:
        print(f"Ошибка при обработке back_to_category ({callback.data}): {e}")
        await callback.answer("❌ Произошла ошибка при возврате к товарам!", show_alert=True)