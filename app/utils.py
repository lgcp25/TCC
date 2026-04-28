# ======================================================
# =========     VALIDAÇÕES E UTILITÁRIOS           =====
# ======================================================

def sanitize(v):
    return "" if v is None else str(v).strip()

def valid_url(url):
    if not url:
        return False
    if " " in url:
        return False
    return True

def valid_port(port):
    if not port.isdigit():
        return False
    p = int(port)
    return 1 <= p <= 65535