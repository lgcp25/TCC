import re

def sanitize(v):
    if v is None:
        return ""
    
    if v.startswith("http://"):
        v = v[len("http://"):]
    elif v.startswith("https://"):
        v = v[len("https://"):]
        
    return v

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

def normalize_logs(raw_logs: str, tool: str = "") -> str:
    if not raw_logs:
        return ""

    lines = raw_logs.splitlines()
    cleaned = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue

        # Remove ANSI escape codes (cores do terminal)
        stripped = re.sub(r'\x1b\[[0-9;]*m', '', stripped)

        # Remove barras de progresso  ex: [========>     ] 45%
        if re.match(r'.*\[=+>?\s*\].*\d+%', stripped):
            continue

        # Remove timestamps repetitivos no início da linha
        stripped = re.sub(r'^\[\d{2}:\d{2}:\d{2}\]\s*', '', stripped)

        if any(banner in stripped.lower() for banner in [
            'projectdiscovery.io', 'sqlmap.org',
            '___', '===', '***',
            'legal disclaimer', 'press enter to continue',
            'starting @ ', 'ending @ '
        ]):
            continue

        if re.match(r'^\[!\]\s*(legal|usage|please)', stripped, re.IGNORECASE):
            continue

        cleaned.append(stripped)


    result = '\n'.join(cleaned).strip()

    return result