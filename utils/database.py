import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey, select
from typing import List, Optional

# Database configuration  
DATABASE_URL = os.getenv("DATABASE_URL", "")
# Fix SSL mode issue by removing sslmode parameter if present
if "?sslmode=" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?sslmode=")[0]
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with proper connection pool settings
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationship
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Relationship
    category: Mapped["Category"] = relationship("Category", back_populates="products")

async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    """Get async database session"""
    async with async_session() as session:
        yield session

# Category operations
async def get_categories() -> List[dict]:
    """Get all categories"""
    async with async_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        return [{"id": cat.id, "name": cat.name} for cat in categories]

async def add_category(name: str) -> int:
    """Add new category"""
    async with async_session() as session:
        category = Category(name=name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category.id

async def delete_category(category_id: int) -> bool:
    """Delete category and all its products"""
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if category:
            await session.delete(category)
            await session.commit()
            return True
        return False

async def update_category(category_id: int, new_name: str) -> bool:
    """Update category name"""
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if category:
            category.name = new_name
            await session.commit()
            return True
        return False

# Product operations
async def get_products() -> List[dict]:
    """Get all products"""
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [
            {
                "id": prod.id,
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "category_id": prod.category_id
            }
            for prod in products
        ]

async def get_products_by_category(category_id: int) -> List[dict]:
    """Get products by category"""
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.category_id == category_id))
        products = result.scalars().all()
        return [
            {
                "id": prod.id,
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "category_id": prod.category_id
            }
            for prod in products
        ]

async def get_product(product_id: int) -> Optional[dict]:
    """Get product by ID"""
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            return {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category_id": product.category_id
            }
        return None

async def add_product(name: str, description: str, price: float, category_id: int) -> int:
    """Add new product"""
    async with async_session() as session:
        product = Product(name=name, description=description, price=price, category_id=category_id)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product.id

async def delete_product(product_id: int) -> bool:
    """Delete product"""
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            await session.delete(product)
            await session.commit()
            return True
        return False

async def update_product(product_id: int, name: str, description: str, price: float) -> bool:
    """Update product"""
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            product.name = name
            product.description = description
            product.price = price
            await session.commit()
            return True
        return False