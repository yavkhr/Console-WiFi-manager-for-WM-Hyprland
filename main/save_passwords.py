import base64
import os

from config import PASSWORD_FILE


def load_passwords():
    passwords = {}
    try:
        lines = PASSWORD_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return passwords
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if not key.startswith("WIFI_PASSWORD_"):
            continue
        try:
            ssid = base64.urlsafe_b64decode(
                key.removeprefix("WIFI_PASSWORD_") + "=="
            ).decode("utf-8")
            password = base64.urlsafe_b64decode(value.strip() + "==").decode(
                "utf-8"
            )
            passwords[ssid] = password
        except (ValueError, UnicodeDecodeError):
            continue
    return passwords


def _store(data):
    try:
        lines = []
        if PASSWORD_FILE.exists():
            lines = [
                line
                for line in PASSWORD_FILE.read_text(encoding="utf-8").splitlines()
                if line.startswith("WIFI_THEME_INDEX=")
            ]
        for ssid, password in sorted(data.items()):
            encoded_ssid = base64.urlsafe_b64encode(ssid.encode()).decode().rstrip("=")
            encoded_password = base64.urlsafe_b64encode(
                password.encode()
            ).decode().rstrip("=")
            lines.append(f"WIFI_PASSWORD_{encoded_ssid}={encoded_password}")
        PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
        PASSWORD_FILE.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        os.chmod(PASSWORD_FILE, 0o600)
    except OSError:
        pass


def get_saved_password(ssid):
    return load_passwords().get(ssid)


def save_password(ssid, password):
    data = load_passwords()
    data[ssid] = password
    _store(data)


def forget_password(ssid):
    data = load_passwords()
    if ssid in data:
        del data[ssid]
        _store(data)
