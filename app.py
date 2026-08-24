import os
import sys
import webbrowser
import asyncio
import socket
import urllib.request
import urllib.parse
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from telethon import TelegramClient, functions, types, errors

try:
    import socks
except ImportError:
    socks = None

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5050))
SESSION_FILE = "user_session"

GIFTS_CATALOG = [
    {"id": "5956217000635139069", "name": "Новогодний мишка",      "stars": 50, "icon": "🧸", "badge": "New Year",    "image": "Новогодний мишка.webp"},
    {"id": "5800655655995968830", "name": "Мишка влюбленных",      "stars": 50, "icon": "🧸", "badge": "Love",        "image": "Мишка влюбленных.webp"},
    {"id": "5922558454332916696", "name": "Елка",                  "stars": 50, "icon": "🎄", "badge": "Holiday",     "image": "Елка.webp"},
    {"id": "5801108895304779062", "name": "Сердце влюбленных",     "stars": 50, "icon": "💝", "badge": "Romantic",    "image": "Сердце влюбленных .webp"},
    {"id": "5866352046986232958", "name": "Мишка на 8 марта",      "stars": 50, "icon": "🧸", "badge": "Spring",      "image": "Мишка на 8 марта.webp"},
    {"id": "5893356958802511476", "name": "Мишка на День Патрика", "stars": 50, "icon": "🧸", "badge": "St. Patrick", "image": "Мишка на День Патрика.webp"},
    {"id": "5935895822435615975", "name": "Мишка на 1 апреля",     "stars": 50, "icon": "🧸", "badge": "Fun",         "image": "Мишка на 1 апреля.webp"},
    {"id": "5969796561943660080", "name": "Мишка на Пасху",        "stars": 50, "icon": "🧸", "badge": "Easter",      "image": "Мишка на Пасху.webp"},
    {"id": "6026193266406327981", "name": "Мишка на 1 мая",        "stars": 50, "icon": "🧸", "badge": "May Day",     "image": "Мишка на 1 мая.webp"},
    {"id": "5974210632977745012", "name": "Мишка на ЧМ",           "stars": 50, "icon": "🧸", "badge": "Sport",       "image": "Мишка на Чемпионат Мира.webp"},
    {"id": "6046178578163303744", "name": "Мишка военный",         "stars": 50, "icon": "🧸", "badge": "Special",     "image": "Мишка военный.webp"},
]

client: Optional[TelegramClient] = None
phone_code_hash: Optional[str] = None
current_phone: Optional[str] = None
_runtime_proxy_config: Optional[dict] = None


def build_proxy_tuple(proxy_type: str, host: str, port: int,
                      username: Optional[str] = None, password: Optional[str] = None):
    if not socks:
        return None
    ptype_str = proxy_type.lower().strip()
    if ptype_str in ["socks5", "socks"]:
        ptype = socks.SOCKS5
    elif ptype_str == "socks4":
        ptype = socks.SOCKS4
    elif ptype_str in ["https", "http"]:
        ptype = socks.HTTP
    else:
        ptype = socks.HTTP

    u = username.strip() if username else None
    p = password.strip() if password else None
    return (ptype, host.strip(), int(port), True, u, p)


def get_detected_proxy():
    global _runtime_proxy_config
    if not socks:
        return None

    if _runtime_proxy_config is not None:
        if not _runtime_proxy_config.get("enabled", True):
            return None
        ptype = _runtime_proxy_config.get("type", "socks5")
        if ptype == "direct":
            return None
        if ptype != "system":
            host = _runtime_proxy_config.get("host")
            port = _runtime_proxy_config.get("port")
            if host and port:
                return build_proxy_tuple(
                    ptype, host, port,
                    _runtime_proxy_config.get("username"),
                    _runtime_proxy_config.get("password")
                )

    env_type = os.getenv("PROXY_TYPE", "").strip()
    env_host = os.getenv("PROXY_HOST", "").strip()
    env_port = os.getenv("PROXY_PORT", "").strip()
    if env_type and env_host and env_port:
        if env_type.lower() == "direct":
            return None
        return build_proxy_tuple(
            env_type, env_host, int(env_port),
            os.getenv("PROXY_USER"), os.getenv("PROXY_PASS")
        )

    env_url = os.getenv("PROXY_URL", "").strip()
    if env_url:
        try:
            parsed = urllib.parse.urlparse(env_url if "://" in env_url else f"http://{env_url}")
            if parsed.hostname and parsed.port:
                scheme = parsed.scheme if parsed.scheme else "http"
                return build_proxy_tuple(
                    scheme, parsed.hostname, parsed.port,
                    parsed.username, parsed.password
                )
        except Exception:
            pass

    local_vpn_candidates = [
        (socks.HTTP, "127.0.0.1", 49544),
        (socks.HTTP, "127.0.0.1", 49543),
        (socks.SOCKS5, "127.0.0.1", 10808),
        (socks.HTTP, "127.0.0.1", 10809),
        (socks.SOCKS5, "127.0.0.1", 2080),
        (socks.SOCKS5, "127.0.0.1", 1080),
        (socks.HTTP, "127.0.0.1", 7890),
    ]
    for p_socktype, l_host, l_port in local_vpn_candidates:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_sock:
                test_sock.settimeout(0.02)
                if test_sock.connect_ex((l_host, l_port)) != 0:
                    continue
        except Exception:
            continue

        s = socks.socksocket()
        s.set_proxy(p_socktype, l_host, l_port)
        s.settimeout(0.5)
        try:
            s.connect(("149.154.167.50", 443))
            s.close()
            p_name = "socks5" if p_socktype == socks.SOCKS5 else "http"
            return build_proxy_tuple(p_name, l_host, l_port)
        except Exception:
            pass

    try:
        proxies = urllib.request.getproxies()
        sys_url = proxies.get("https") or proxies.get("http")
        if sys_url:
            parsed = urllib.parse.urlparse(sys_url if "://" in sys_url else f"http://{sys_url}")
            if parsed.hostname and parsed.port:
                scheme = parsed.scheme if parsed.scheme else "http"
                return build_proxy_tuple(
                    scheme, parsed.hostname, parsed.port,
                    parsed.username, parsed.password
                )
    except Exception:
        pass

    return None


async def get_or_create_client(api_id: int, api_hash: str, force_recreate: bool = False) -> TelegramClient:
    global client
    proxy = get_detected_proxy()
    if client is not None and force_recreate:
        try:
            if client.is_connected():
                await client.disconnect()
        except Exception:
            pass
        client = None

    if client is None:
        client = TelegramClient(
            SESSION_FILE,
            api_id,
            api_hash,
            proxy=proxy,
            timeout=12,
            connection_retries=3
        )
    if not client.is_connected():
        await client.connect()
    return client


async def get_stars_balance(tg_client: TelegramClient) -> int:
    try:
        status = await tg_client(functions.payments.GetStarsStatusRequest(peer=types.InputPeerSelf()))
        balance = getattr(status.balance, "amount", status.balance)
        return int(balance)
    except Exception:
        return -1


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    async def try_connect():
        global client
        if API_ID and API_HASH and str(API_ID).strip() and str(API_HASH).strip():
            try:
                client = await get_or_create_client(int(API_ID), API_HASH)
                if await client.is_user_authorized():
                    me = await client.get_me()
                    print(f"[+] Authorized as: {me.first_name} (@{me.username})")
            except Exception as e:
                print(f"[*] Connection info: {e}")

    asyncio.create_task(try_connect())
    yield
    if client and client.is_connected():
        await client.disconnect()


BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(title="Telegram Star Gifts Sender", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class AuthSendCodeReq(BaseModel):
    api_id: int
    api_hash: str
    phone: str


class AuthSignInReq(BaseModel):
    code: str
    password: Optional[str] = None


class SendGiftReq(BaseModel):
    target_user: str
    gift_id: str
    message: Optional[str] = ""
    hide_name: bool = False


class ProxyConfigReq(BaseModel):
    enabled: bool = True
    proxy_type: str = "socks5"
    host: Optional[str] = "127.0.0.1"
    port: Optional[int] = 1080
    username: Optional[str] = None
    password: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "gifts": GIFTS_CATALOG,
            "default_api_id": API_ID or "",
            "default_api_hash": API_HASH or "",
        },
    )


@app.get("/api/status")
async def get_auth_status():
    global client
    if client is None and API_ID and API_HASH and str(API_ID).strip() and str(API_HASH).strip():
        try:
            client = await get_or_create_client(int(API_ID), API_HASH)
        except Exception:
            return {"authorized": False}

    if client:
        try:
            if not client.is_connected():
                await asyncio.wait_for(client.connect(), timeout=3.0)
            is_auth = await asyncio.wait_for(client.is_user_authorized(), timeout=3.0)
            if is_auth:
                me = await client.get_me()
                balance = await get_stars_balance(client)
                return {
                    "authorized": True,
                    "user": {
                        "id": me.id,
                        "first_name": me.first_name,
                        "username": me.username,
                        "phone": me.phone
                    },
                    "balance": balance
                }
        except Exception:
            pass
    return {"authorized": False}


@app.get("/api/proxy")
async def get_proxy_info():
    current_tuple = get_detected_proxy()
    readable_type = "none"
    readable_host = ""
    readable_port = 0
    if current_tuple:
        ptype, host, port, _, _, _ = current_tuple
        type_names = {socks.SOCKS5: "SOCKS5", socks.SOCKS4: "SOCKS4", socks.HTTP: "HTTP/HTTPS"}
        readable_type = type_names.get(ptype, "PROXY")
        readable_host = host
        readable_port = port

    return {
        "active": current_tuple is not None,
        "type": readable_type,
        "host": readable_host,
        "port": readable_port,
        "runtime_config": _runtime_proxy_config
    }


@app.post("/api/proxy")
async def set_proxy_info(req: ProxyConfigReq):
    global _runtime_proxy_config, client
    _runtime_proxy_config = {
        "enabled": req.enabled,
        "type": req.proxy_type.lower(),
        "host": req.host.strip() if req.host else "",
        "port": req.port or 0,
        "username": req.username.strip() if req.username else "",
        "password": req.password.strip() if req.password else ""
    }

    if client is not None:
        try:
            if client.is_connected():
                asyncio.create_task(client.disconnect())
        except Exception:
            pass
        client = None

    return {"success": True, "proxy": await get_proxy_info()}


@app.post("/api/proxy/test")
async def test_proxy_endpoint(req: ProxyConfigReq):
    if not socks:
        return {"success": False, "error": "PySocks not installed"}

    ptype = req.proxy_type.lower()
    if ptype == "direct":
        return {"success": True, "message": "Прямое подключение"}

    sock_type = socks.SOCKS5 if ptype == "socks5" else socks.HTTP
    host = req.host.strip() if req.host else ""
    port = int(req.port or 0)
    user = req.username.strip() if req.username else None
    password = req.password.strip() if req.password else None

    if not host or not port:
        return {"success": False, "error": "Укажите хост и порт"}

    def _test():
        s = socks.socksocket()
        s.set_proxy(sock_type, host, port, username=user, password=password)
        s.settimeout(5.0)
        try:
            s.connect(("149.154.167.50", 443))
            s.close()
            return True, "Связь с серверами Telegram установлена."
        except Exception as e:
            err_msg = str(e)
            if "timed out" in err_msg:
                err_msg = "Таймаут соединения с прокси"
            elif "HTTP proxy" in err_msg or "invalid response" in err_msg:
                err_msg = "Неверный тип прокси или логин/пароль"
            return False, f"Ошибка прокси: {err_msg}"

    loop = asyncio.get_event_loop()
    ok, msg = await loop.run_in_executor(None, _test)
    return {"success": ok, "message": msg}


@app.post("/api/auth/send_code")
async def send_code(req: AuthSendCodeReq):
    global current_phone, phone_code_hash
    try:
        phone_cleaned = req.phone.strip().replace(" ", "").replace("-", "")
        tg = await get_or_create_client(req.api_id, req.api_hash)
        sent = await asyncio.wait_for(tg.send_code_request(phone_cleaned), timeout=15.0)
        phone_code_hash = sent.phone_code_hash
        current_phone = phone_cleaned
        return {"success": True, "message": f"Код подтверждения отправлен на номер {phone_cleaned} в Telegram!"}
    except errors.PhoneNumberInvalidError:
        return JSONResponse(status_code=400, content={"error": "Неверный номер телефона."})
    except errors.FloodWaitError as e:
        return JSONResponse(status_code=400, content={"error": f"FloodWait: подождите {e.seconds} сек."})
    except asyncio.TimeoutError:
        return JSONResponse(status_code=500, content={"error": "Таймаут подключения к Telegram. Проверьте прокси/VPN."})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Ошибка отправки кода: {str(e)}"})


@app.post("/api/auth/sign_in")
async def sign_in(req: AuthSignInReq):
    global client, current_phone, phone_code_hash
    if not client or not current_phone or not phone_code_hash:
        return JSONResponse(status_code=400, content={"error": "Сначала запросите код в Telegram"})
    try:
        code_cleaned = req.code.strip().replace(" ", "")
        try:
            await client.sign_in(current_phone, code_cleaned, phone_code_hash=phone_code_hash)
        except errors.SessionPasswordNeededError:
            if not req.password:
                return {"requires_password": True, "message": "Требуется 2FA пароль"}
            await client.sign_in(password=req.password)

        me = await client.get_me()
        balance = await get_stars_balance(client)
        return {
            "success": True,
            "user": {
                "id": me.id,
                "first_name": me.first_name,
                "username": me.username
            },
            "balance": balance
        }
    except errors.PhoneCodeInvalidError:
        return JSONResponse(status_code=400, content={"error": "Неверный код подтверждения"})
    except errors.PhoneCodeExpiredError:
        return JSONResponse(status_code=400, content={"error": "Срок действия кода истёк."})
    except errors.PasswordHashInvalidError:
        return JSONResponse(status_code=400, content={"error": "Неверный 2FA пароль"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Ошибка входа: {str(e)}"})


@app.post("/api/auth/logout")
async def logout():
    global client
    if client and client.is_connected():
        await client.log_out()
    return {"success": True}


@app.get("/api/user/resolve")
async def resolve_user(query: str):
    global client
    if not client or not await client.is_user_authorized():
        return JSONResponse(status_code=401, content={"error": "Не авторизован"})
    q = query.strip().lstrip("@")
    if not q:
        return {"success": False, "error": "Пустой запрос"}
    try:
        entity = await client.get_entity(q)
        first_name = getattr(entity, "first_name", "") or ""
        last_name = getattr(entity, "last_name", "") or ""
        full_name = f"{first_name} {last_name}".strip() or getattr(entity, "title", q)
        username = getattr(entity, "username", None)
        user_id = getattr(entity, "id", None)
        is_bot = getattr(entity, "bot", False)
        return {
            "success": True,
            "id": user_id,
            "name": full_name,
            "username": f"@{username}" if username else None,
            "is_bot": is_bot
        }
    except Exception:
        return {"success": False, "error": "Пользователь не найден"}


@app.post("/api/gifts/send")
async def send_gift(req: SendGiftReq):
    global client
    if not client or not await client.is_user_authorized():
        return JSONResponse(status_code=401, content={"error": "Пользователь не авторизован"})

    try:
        target_peer = await client.get_input_entity(req.target_user)
        target_entity = await client.get_entity(req.target_user)
        recipient_name = getattr(target_entity, "first_name", "") or getattr(target_entity, "title", req.target_user)

        parsed_gift_id = int(str(req.gift_id).strip())
        msg_obj = types.TextWithEntities(text=req.message, entities=[]) if req.message else None

        invoice = types.InputInvoiceStarGift(
            peer=target_peer,
            gift_id=parsed_gift_id,
            hide_name=True if req.hide_name else None,
            message=msg_obj
        )

        form = await client(functions.payments.GetPaymentFormRequest(invoice=invoice))
        await client(functions.payments.SendStarsFormRequest(
            form_id=form.form_id,
            invoice=invoice
        ))

        new_balance = await get_stars_balance(client)
        return {
            "success": True,
            "recipient": recipient_name,
            "new_balance": new_balance,
            "message": f"Подарок успешно отправлен для {recipient_name}!"
        }
    except errors.RPCError as e:
        msg = str(e)
        if "STARGIFT_INVALID" in msg or "STARGIFT_ID_INVALID" in msg:
            msg = f"ID подарка ({req.gift_id}) недоступен в Telegram."
        elif "STARGIFT_USAGE_LIMITED" in msg:
            msg = "Лимит данного подарка исчерпан (Sold Out)"
        elif "BALANCE_TOO_LOW" in msg or "BALANCE_LOW" in msg:
            msg = "Недостаточно Telegram Stars на вашем балансе"
        elif "PEER_ID_INVALID" in msg or "USERNAME_NOT_OCCUPIED" in msg or "USERNAME_INVALID" in msg:
            msg = f"Получатель '{req.target_user}' не найден"
        elif "USER_PRIVACY_RESTRICTED" in msg:
            msg = f"Пользователь '{req.target_user}' запретил дарить подарки в настройках приватности"
        return JSONResponse(status_code=400, content={"error": msg})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Ошибка отправки: {str(e)}"})


def find_free_port(host: str, start_port: int) -> int:
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


if __name__ == "__main__":
    import uvicorn
    try:
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    active_port = find_free_port(HOST, PORT)
    url = f"http://{HOST}:{active_port}"
    print(f"[*] Server starting on: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    uvicorn.run(app, host=HOST, port=active_port)
