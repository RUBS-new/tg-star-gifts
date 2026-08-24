<div align="center">

# 🎁 Telegram Star Gifts Sender

**Modern Web UI for sending Telegram Star Gifts via MTProto**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Telethon](https://img.shields.io/badge/Telethon-1.36+-2BA3E3?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.telethon.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

[English](#-english) &bull; [Русский](#-русский)

</div>

---

## 🇬🇧 English

A full-featured Web UI and MTProto client for sending Telegram gifts with Telegram Stars directly through official Telegram DC endpoints.

### ✨ Features

- 🧸 **Built-in Gift Catalog**: 11 popular seasonal and holiday gifts (50 Stars each) + support for custom gift IDs.
- 🛡️ **Accidental Spend Protection**: Confirmation modal displaying recipient details, gift summary, and exact Star cost before charging.
- 🎯 **Recipient Live Preview**: Instant name, `@username`, and user ID validation as you type.
- 🌐 **Proxy & VPN Support**: Built-in SOCKS5 / HTTPS proxy settings, DC connectivity tester, and automatic detection of local VPN clients.
- ⭐️ **Live Star Balance**: Real-time Telegram Stars balance indicator.
- 🔒 **Anonymous Gifts**: Option to hide sender identity.
- 💬 **Custom Message**: Attach text greetings to your gifts.
- 🎉 **Confetti Animation**: Celebration effects upon successful delivery.
- 📱 **Integrated Auth**: Telegram phone authorization with 2FA password support.

### 🚀 Quick Start

#### Option 1: 1-Click Launch (Windows)
Just double-click **`start.bat`**. It will automatically set up the virtual environment, install dependencies, and launch the web interface.

#### Option 2: Manual Installation
```bash
git clone https://github.com/RUBS-new/tg-star-gifts.git
cd tg-star-gifts
pip install -r requirements.txt
python app.py
```

Open **`http://127.0.0.1:5050`** in your browser.

### ⚙️ Configuration

Copy `.env.example` to `.env` (optional):
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
HOST=127.0.0.1
PORT=5050
```
> API credentials can be obtained from [my.telegram.org](https://my.telegram.org). You can also enter them directly in the Web UI.

---

## 🇷🇺 Русский

Веб-приложение и панель управления для отправки эксклюзивных подарков в Telegram за звёзды (**Telegram Stars**) напрямую через официальный протокол **MTProto**.

### ✨ Возможности

- 🧸 **Каталог подарков**: 11 сезонных и праздничных подарков (по 50 Stars) + поддержка любого кастомного Gift ID.
- 🛡️ **Защита от случайных списаний**: всплывающее модальное окно подтверждения с деталями подарка и точной суммой перед оплатой.
- 🎯 **Live Preview получателя**: автоопределение имени, `@username` и ID пользователя при вводе.
- 🌐 **Поддержка Прокси и VPN**: настройка SOCKS5 / HTTPS прокси, проверка связи с Telegram DC и автодетект активного локального VPN.
- ⭐️ **Баланс Stars в реальном времени**: отображение актуального количества звёзд на аккаунте.
- 🔒 **Анонимная отправка**: возможность скрыть имя отправителя при подарке.
- 💬 **Текстовые поздравления**: прикрепление сообщений к подарку.
- 🎉 **Праздничный салют**: анимация конфетти и звёздного дождя при успешной доставке.
- 📱 **Встроенная авторизация**: вход по номеру телефона, коду из Telegram и 2FA паролю.

### 🚀 Быстрый запуск

#### Вариант 1: Запуск в 1 клик (Windows)
Просто дважды кликните по файлу **`start.bat`**. Он сам создаст окружение, установит нужные библиотеки и откроет сайт в браузере.

#### Вариант 2: Запуск через консоль
```bash
git clone https://github.com/RUBS-new/tg-star-gifts.git
cd tg-star-gifts
pip install -r requirements.txt
python app.py
```

Откройте в браузере: **`http://127.0.0.1:5050`**

### ⚙️ Настройка

Скопируйте `.env.example` в `.env` (необязательно):
```env
TELEGRAM_API_ID=20347001
TELEGRAM_API_HASH=63034eed446c764c7d09ba7b15f88934
HOST=127.0.0.1
PORT=5050
```
> `API_ID` и `API_HASH` можно получить на [my.telegram.org](https://my.telegram.org) или ввести прямо в интерфейсе при первом входе.

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **Telegram MTProto**: Telethon
- **Frontend**: HTML5, Tailwind CSS, FontAwesome 6, Canvas Confetti
- **Networking**: PySocks (SOCKS5 / HTTP / HTTPS)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
