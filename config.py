import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # Replace with actual admin user ID

# Seller contact information
SELLER_CONTACT = os.getenv("SELLER_CONTACT", "@seller_username")
GROUP = os.getenv("GROUP", "null")
# Data file paths
CATEGORIES_FILE = "data/categories.json"
PRODUCTS_FILE = "data/products.json"

# Messages
WELCOME_MESSAGE = """Приветствуем вас в нашем онлайн-магазине 🛍️!

Euphoria — ваш надежный источник выгодных цен на электронные сигареты, жидкости и расходники. Широкий ассортимент качественной продукции, постоянные акции и новинки для вашего удовольствия и экономии!

✅ Ознакомьтесь с нашими категориями товаров и выберите идеальный продукт под ваши запросы.

👉 Перейдите также в нашу группу с отзывами покупателей, где регулярно публикуются объявления о проводимых акциях, скидках и распродажах. Узнавайте первыми о специальных предложениях и выгодах!

Делайте выбор вместе с Euphoria и наслаждайтесь качественным парением каждый день!"""

ADMIN_WELCOME_MESSAGE = """
👑 Панель администратора

Выберите действие:
"""

ORDER_MESSAGE = """
📞 Для оформления заказа свяжитесь с продавцом:
{contact}
"""
