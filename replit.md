# Overview

A Telegram bot for an e-commerce store built with Python and the aiogram framework. The bot allows users to browse product categories, view products, and contact sellers for orders. It includes an admin panel for managing categories and products, with data persistence using PostgreSQL database. The bot features a persistent menu for easy navigation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **aiogram v3**: Modern asynchronous Telegram bot framework for Python
- **FSM (Finite State Machine)**: Uses MemoryStorage for handling user states and conversations
- **Router-based handlers**: Modular approach separating user and admin functionality

## Data Storage
- **PostgreSQL database**: Categories and products stored in PostgreSQL database tables
- **SQLAlchemy ORM**: Modern async ORM for database operations with declarative models
- **Auto-incrementing IDs**: Database-generated primary keys for categories and products
- **Foreign key constraints**: Referential integrity between categories and products
- **Async sessions**: Non-blocking database I/O using async SQLAlchemy sessions

## Application Structure
- **Modular handlers**: Separate routers for user interactions and admin operations
- **Inline keyboards**: Dynamic keyboard generation based on available categories and products
- **Callback query routing**: Event-driven navigation using callback data patterns
- **Persistent menu**: Bottom menu with buttons for quick access to catalog and admin panel
- **HTML formatting**: Proper text formatting using HTML tags instead of markdown

## Configuration Management
- **Environment variables**: Bot token and admin ID configured via environment
- **Centralized config**: All settings and messages defined in config.py
- **Flexible seller contact**: Configurable seller contact information

## Message Flow
- **Category browsing**: Hierarchical navigation from categories to products
- **Product details**: Individual product information display
- **Order routing**: Direct users to seller contact for purchases
- **Admin commands**: Protected admin functionality for content management

## Error Handling
- **Logging system**: Comprehensive logging for debugging and monitoring
- **Graceful degradation**: Fallback messages when no data is available
- **Session cleanup**: Proper bot session management

# External Dependencies

## Core Framework
- **aiogram**: Telegram Bot API wrapper for Python
- **asyncio**: Python's built-in asynchronous programming library

## Data Storage
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: Modern Python SQL toolkit and ORM
- **asyncpg**: Async PostgreSQL driver for Python (used by SQLAlchemy)

## Telegram Integration
- **Telegram Bot API**: Direct integration via bot token
- **Inline keyboards**: Native Telegram UI components
- **Callback queries**: Telegram's callback mechanism for interactive buttons

## Development Tools
- **Python logging**: Built-in logging module for application monitoring
- **Environment variables**: Standard environment-based configuration