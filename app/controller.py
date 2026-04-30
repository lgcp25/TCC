import flet as ft
import os
import asyncio
import subprocess
import logging
from config import THEME_BG, THEME_CARD, THEME_BORDER, DOCKER_DIR
from ui.tabs import (
    NmapTab, SqlmapTab, NucleiTab, NiktoTab, GobusterTab, 
    DirsearchTab, CommixTab, NetcatTab, MetasploitTab
)
from services.docker_runner import run_docker, cancel_process

logger = logging.getLogger(__name__)

class PentesterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Vaporeon - Pentester Suite"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = THEME_BG
        self.page.padding = 0
        # Tenta maximizar a janela, se não conseguir não mostra erro
        try: self.page.window_maximized = True
        except: pass
        
        # Configura a fonte
        self.page.fonts = {
            "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
        }
        
        # Lista de resultados para incluir no relatório final
        self.report_findings = []
        # Dicionário para guardar as instâncias das abas das ferramentas
        self.tools = {}
        # Monitoramento de serviços
        self._monitoring = True
        # Botão ativo
        self._active_tool_btn = None
        # Cookies do DVWA para autenticação automática, no formato 'key=value; key=value'
        self.dvwa_cookies = {}

    # Método de inicialização da aplicação
    async def initialize(self):
        from ui.header import HeaderPanel
        
        # Cria a barra de ferramentas a partir do novo componente
        self.tab_header = HeaderPanel(self)

        # Instâncias das abas das ferramentas
        self.nmap_tab = NmapTab(self, "Nmap")
        self.sqlmap_tab = SqlmapTab(self, "Sqlmap")
        self.nuclei_tab = NucleiTab(self, "Nuclei")
        self.nikto_tab = NiktoTab(self, "Nikto")
        self.gobuster_tab = GobusterTab(self, "Gobuster")
        self.dirsearch_tab = DirsearchTab(self, "Dirsearch")
        self.commix_tab = CommixTab(self, "Commix")
        self.netcat_tab = NetcatTab(self, "Netcat")
        self.metasploit_tab = MetasploitTab(self, "Metasploit")

        # Dicionário para guardar as instâncias das abas das ferramentas para manter o histórico de scans
        self.tools = {
            "Nmap": self.nmap_tab,
            "Sqlmap": self.sqlmap_tab,
            "Nuclei": self.nuclei_tab,
            "Nikto": self.nikto_tab,
            "Gobuster": self.gobuster_tab,
            "Dirsearch": self.dirsearch_tab,
            "Commix": self.commix_tab,
            "Netcat": self.netcat_tab,
            "Metasploit": self.metasploit_tab,
        }
        # Área de conteúdo principal - começa com a aba do Nmap
        self.content_area = ft.Container(content=self.nmap_tab.view, expand=True)

        # Adiciona todo o conteúdo à página
        self.page.add(
            ft.Column([
                self.tab_header,
                self.content_area
            ], expand=True, spacing=0)
        )

        # Carrega barra de progresso inicial - self.loader
        self.set_loading("Iniciando Infraestrutura Docker...", True)

        # Sobe o Docker-compose e inicia o DVWA
        try:
            try: subprocess.Popen(["docker-compose", "up", "-d"], cwd=DOCKER_DIR)
            # Tenta novamente com "docker" em vez de "docker-compose"
            except Exception: subprocess.Popen(["docker", "compose", "up", "-d"], cwd=DOCKER_DIR)
            
            # Dispara auto-setup do DVWA no background (login e cria banco)
            from services.dvwa_service import wait_and_init_dvwa
            async def run_setup():
                cookies = await wait_and_init_dvwa()
                if cookies:
                    self.dvwa_cookies = cookies
                    logger.info(f"Cookies capturados: {self.dvwa_cookies}")
            
            asyncio.ensure_future(run_setup())
            
            await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"Falha ao iniciar Docker: {e}")
        self.set_loading("", False)

        # Inicia monitoramento em background
        asyncio.ensure_future(self._monitor_services())

    # Monitora os serviços em background verifica o status dos containers a cada 10 segundos
    async def _monitor_services(self):
        while self._monitoring:
            try:
                # Checar containers Docker
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}"],
                    capture_output=True, text=True, timeout=5
                )
                running = result.stdout.lower() if result.returncode == 0 else ""
                
                self.tab_header.svc_pentester.color = "green" if "pentester" in running else "red"
                self.tab_header.svc_dvwa.color = "green" if "dvwa" in running else "red"
                self.tab_header.svc_metasploit.color = "green" if "metasploit" in running else "red"
                
                # Checar Groq API (verifica se a chave existe)
                groq_key = os.getenv("GROQ_API_KEY", "")
                self.tab_header.svc_groq.color = "green" if groq_key else "red"

                self.tab_header.svc_pentester.update()
                self.tab_header.svc_dvwa.update()
                self.tab_header.svc_groq.update()

            # Se der erro, ignora e continua    
            except:
                pass
            # Espera 10 segundos antes de verificar novamente impede o app de travar
            await asyncio.sleep(10)

    # Método que alterna o painel conforme o botão clicado pelo usuário
    def switch_tool(self, tool_name):
        if tool_name in self.tools:
            self.content_area.content = self.tools[tool_name].view
            self.content_area.update()

    # Método que exibe uma mensagem do status e uma barra de progresso
    def set_loading(self, status, visible=True):
        self.tab_header.status_text.value = status
        self.tab_header.loader.visible = visible
        self.tab_header.status_text.update()
        self.tab_header.loader.update()

    # Método que executa o comando no container
    async def run_docker(self, container, cmd, on_output, tab=None):
        self.set_loading("Scanner em execução...")
        await run_docker(tab or self, container, cmd, on_output)
        self.set_loading("", False)

    # Método que cancela o comando no container
    def cancel_process(self, on_output=None, tab=None):
        cancel_process(tab or self, on_output)
        self.set_loading("Interrompido", False)
