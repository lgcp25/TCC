# ======================================================
# =========     VALIDAÇÕES E UTILITÁRIOS           =====
# ======================================================
import re

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

def normalize_logs(raw_logs: str, tool: str = "") -> str:
    """Remove ruído dos logs antes de enviar à IA, preservando dados valiosos.
    
    Filtra: ANSI codes, banners, barras de progresso, timestamps repetitivos,
    linhas vazias em excesso e limita o tamanho total para não estourar o contexto.
    """
    if not raw_logs:
        return ""

    lines = raw_logs.splitlines()
    cleaned = []

    for line in lines:
        stripped = line.strip()

        # Remove linhas vazias em sequência (mantém no máximo 1)
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
        # Ex: "[15:30:01] [INFO] testing..." → "[INFO] testing..."
        stripped = re.sub(r'^\[\d{2}:\d{2}:\d{2}\]\s*', '', stripped)

        # Remove banners / arte ASCII / linhas decorativas das ferramentas
        if any(banner in stripped.lower() for banner in [
            'projectdiscovery.io', 'sqlmap.org',
            '___', '===', '***',
            'legal disclaimer', 'press enter to continue',
            'starting @ ', 'ending @ '
        ]):
            continue

        # Remove linhas puramente informativas sem conteúdo analítico
        if re.match(r'^\[!\]\s*(legal|usage|please)', stripped, re.IGNORECASE):
            continue

        cleaned.append(stripped)

    # Remove linhas vazias do início e fim
    result = '\n'.join(cleaned).strip()

    # Limita tamanho para não estourar contexto (últimas N linhas se muito grande)
    max_lines = 150
    final_lines = result.splitlines()
    if len(final_lines) > max_lines:
        result = '\n'.join(final_lines[-max_lines:])
        result = f"[... {len(final_lines) - max_lines} linhas anteriores omitidas ...]\n" + result

    return result