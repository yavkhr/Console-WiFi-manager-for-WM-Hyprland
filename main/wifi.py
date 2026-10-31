import subprocess

NMCLI = "nmcli"
PASS_TIMEOUT = 45


def nmcli(*args, timeout=15):
    try:
        p = subprocess.run(
            [NMCLI, *args], capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "превышено время ожидания"


def split_fields(line):
    fields, cur, esc = [], [], False
    for ch in line:
        if esc:
            cur.append(ch)
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == ":":
            fields.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    fields.append("".join(cur))
    return fields


def wifi_device():
    rc, out, _ = nmcli("-g", "DEVICE,TYPE", "device", "status")
    if rc != 0:
        return None
    for line in out.splitlines():
        f = split_fields(line)
        if len(f) >= 2 and f[1] in ("wifi", "802-11-wireless"):
            return f[0]
    return None


def scan(dev):
    rc, out, _ = nmcli(
        "-g", "IN-USE,SSID,SIGNAL,SECURITY",
        "device", "wifi", "list", "ifname", dev,
        timeout=20,
    )
    nets = {}
    if rc == 0:
        for line in out.splitlines():
            f = split_fields(line)
            if len(f) < 4:
                continue
            in_use, ssid, signal, sec = f[0], f[1], f[2], f[3]
            if not ssid:
                continue
            try:
                sig = int(signal)
            except ValueError:
                sig = 0
            if ssid not in nets or sig > nets[ssid]["signal"]:
                nets[ssid] = {
                    "ssid": ssid,
                    "signal": sig,
                    "sec": sec,
                    "in_use": in_use == "*",
                }
    return sorted(nets.values(), key=lambda n: (not n["in_use"], -n["signal"]))


def rescan(dev):
    nmcli("device", "wifi", "rescan", "ifname", dev, timeout=6)


def active_profile(dev):
    rc, out, _ = nmcli("-g", "GENERAL.CONNECTION", "device", "show", dev)
    if rc != 0 or not out.strip():
        return None
    return out.strip()


def active_ssid(dev):
    profile = active_profile(dev)
    if not profile:
        return None
    rc, out, _ = nmcli("-g", "802-11-wireless.ssid", "connection", "show", profile)
    if rc != 0:
        return None
    ssid = out.strip()
    if "\\" in ssid:
        ssid = ssid.replace("\\:", ":")
        ssid = ssid.replace("\\\\", "\\")
    return ssid or None


def connect(ssid, password=None):
    args = ["device", "wifi", "connect", ssid]
    if password is not None:
        args += ["password", password]
    return nmcli(*args, timeout=PASS_TIMEOUT)


def disconnect(dev):
    return nmcli("device", "disconnect", dev, timeout=15)[0]
