import asyncio
import logging
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


DVWA_URL = "http://localhost:8081"


def _get_token(session, url):
    """Obtém o token CSRF da página, necessário no DVWA."""
    response = session.get(url)
    match = re.search(r"name='user_token' value='([a-f0-9]+)'", response.text)
    return match.group(1) if match else None

def _init_dvwa_sync():
    """Lógica síncrona para inicializar o DVWA. Roda em thread separada.
    
    Sempre usa uma sessão limpa para evitar conflito com PHPSESSID de reinícios anteriores.
    """
    # Sessão limpa — sem cookies antigos que causariam 403/redirect incorreto
    session = requests.Session()
    session.cookies.clear()
    session.headers.update({"Host": "dvwa"})
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        logger.info("Realizando Auto-Login no DVWA...")
        login_url = f"{DVWA_URL}/login.php"
        token = _get_token(session, login_url)

        if token:
            # DVWA está na tela de login — faz login normalmente
            login_data = {
                "username": "admin",
                "password": "password",
                "Login": "Login",
                "user_token": token
            }
            session.post(login_url, data=login_data)
        else:
            # Token não encontrado: DVWA pode já estar logado (sessão ativa)
            # Tenta acessar setup.php diretamente para verificar
            logger.warning("Token CSRF não encontrado na página de login. Tentando prosseguir sem login explícito.")

        logger.info("Criando/Resetando Banco de Dados do DVWA...")
        setup_url = f"{DVWA_URL}/setup.php"
        setup_token = _get_token(session, setup_url)
        if setup_token:
            setup_data = {
                "create_db": "Create / Reset Database",
                "user_token": setup_token
            }
            session.post(setup_url, data=setup_data)
        else:
            logger.warning("Token de setup não encontrado — banco pode já estar configurado.")

        logger.info("Configurando Segurança do DVWA para 'Low'...")
        sec_url = f"{DVWA_URL}/security.php"
        sec_token = _get_token(session, sec_url)
        if sec_token:
            sec_data = {
                "security": "low",
                "seclev_submit": "Submit",
                "user_token": sec_token
            }
            session.post(sec_url, data=sec_data)

        cookies = session.cookies.get_dict()
        phpsessid = cookies.get("PHPSESSID")

        if not phpsessid:
            logger.error("PHPSESSID não obtido após login. DVWA pode não ter respondido corretamente.")
            return None

        logger.info(f"DVWA pronto para Pentest! PHPSESSID={phpsessid}")
        return {
            "PHPSESSID": phpsessid,
            "security": cookies.get("security", "low")
        }

    except requests.exceptions.ConnectionError:
        logger.error("Não foi possível conectar ao DVWA. O Docker está rodando?")
        return None
    except Exception as e:
        logger.error(f"Erro ao configurar DVWA: {e}")
        return None

async def wait_and_init_dvwa():

    for i in range(15):

        try:

            response = requests.get(
                f"{DVWA_URL}/login.php",
                timeout=3
            )

            if response.status_code == 200:

                logger.info(
                    "DVWA disponível."
                )

                return await asyncio.to_thread(
                    _init_dvwa_sync
                )

        except Exception:
            pass

        logger.info(
            f"Aguardando DVWA... tentativa {i+1}"
        )

        await asyncio.sleep(2)

    logger.error(
        "Timeout aguardando DVWA."
    )

    return None
