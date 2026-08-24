import asyncio
import os
import sys
import urllib.request
import urllib.parse
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

try:
    import socks
except ImportError:
    socks = None

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0")) if os.getenv("TELEGRAM_API_ID") else 0
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_FILE = "user_session"


def build_proxy_tuple(proxy_type: str, host: str, port: int, username=None, password=None):
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
    return (ptype, host.strip(), int(port), True, username or None, password or None)


def get_detected_proxy():
    if not socks:
        return None

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


async def interactive_login():
    try:
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=== Telegram Login ===")

    proxy = get_detected_proxy()
    if proxy:
        ptype_names = {socks.SOCKS5: "SOCKS5", socks.SOCKS4: "SOCKS4", socks.HTTP: "HTTP/HTTPS"}
        p_label = ptype_names.get(proxy[0], "PROXY")
        print(f"[*] Proxy: {p_label} ({proxy[1]}:{proxy[2]})")
    else:
        print("[*] Direct connection")

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH, proxy=proxy, timeout=12)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"[+] Already authorized: {me.first_name} (@{me.username or 'no username'})")
        await client.disconnect()
        return

    phone = input("Phone number (+...): ").strip().replace(" ", "").replace("-", "")
    if not phone:
        print("[-] Phone number is required")
        await client.disconnect()
        return

    print(f"[*] Sending code to {phone}...")
    try:
        sent_code = await client.send_code_request(phone)
        print("[+] Code sent")
    except Exception as e:
        print(f"[-] Error: {e}")
        await client.disconnect()
        return

    code = input("Code: ").strip().replace(" ", "")
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=sent_code.phone_code_hash)
    except SessionPasswordNeededError:
        pwd = input("2FA Password: ").strip()
        await client.sign_in(password=pwd)
    except Exception as e:
        print(f"[-] Login failed: {e}")
        await client.disconnect()
        return

    me = await client.get_me()
    print(f"[+] Authorized as {me.first_name} (@{me.username or 'none'}), ID: {me.id}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(interactive_login())
