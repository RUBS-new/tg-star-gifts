# tg-star-gifts

Web UI for sending Telegram Star Gifts via MTProto (Telethon + FastAPI).

## Features

- 11 built-in gifts catalog (50 Stars each) + custom gift ID input
- Send confirmation modal with cost and recipient info
- Recipient live preview (resolves name, @username, user ID)
- SOCKS5 and HTTP/HTTPS proxy support + local VPN auto-detection
- Real-time Telegram Stars balance display
- Optional anonymous sending (hide sender name) and gift message
- Built-in Telegram authorization (phone code + 2FA)

## Installation

```bash
git clone https://github.com/RUBS-new/tg-star-gifts.git
cd tg-star-gifts
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env`:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
HOST=127.0.0.1
PORT=5050
```

> API credentials can be obtained from [my.telegram.org](https://my.telegram.org). You can also enter them directly in the Web UI.

## Usage

Start the web server:

```bash
python app.py
```

Or on Windows: double-click `start.bat`.

Open [http://127.0.0.1:5050](http://127.0.0.1:5050) in your browser.

## License

MIT
