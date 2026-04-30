import flet as ft
import os
import asyncio
import subprocess
import logging
from config import THEME_BG, THEME_CARD, THEME_BORDER, DOCKER_DIR
from ui.nmap_tab import NmapTab
from ui.sqlmap_tab import SqlmapTab
from ui.nuclei_tab import NucleiTab
from ui.nikto_tab import NiktoTab
from ui.gobuster_tab import GobusterTab
from ui.dirsearch_tab import DirsearchTab
from ui.commix_tab import CommixTab
from ui.netcat_tab import NetcatTab
from ui.metasploit_tab import MetasploitTab
from services.docker_runner import run_docker, cancel_process

logger = logging.getLogger(__name__)

class PentesterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Pentester Suite — Ultimate Edition"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = THEME_BG
        self.page.padding = 0
        try: self.page.window_maximized = True
        except: pass
        
        self.page.fonts = {
            "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
        }
        
        self.report_findings = []
        self.tools = {}
        self._monitoring = True
        self._active_tool_btn = None
        self.dvwa_cookies = {}

    async def initialize(self):
        # Loader e Status
        self.loader = ft.ProgressBar(width=200, color="amber", visible=False)
        self.status_text = ft.Text("", size=11, italic=True, color="amber")

        # Indicadores de Serviços
        self.svc_pentester = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_dvwa = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_metasploit = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_groq = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)

        services_panel = ft.Row([
            ft.Row([self.svc_pentester, ft.Text("Pentester", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_dvwa, ft.Text("DVWA", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_metasploit, ft.Text("Metasploit", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_groq, ft.Text("Groq API", size=10, color="blueGrey300")], spacing=4),
        ], spacing=15)

        # Botões de navegação das ferramentas
        self.tool_buttons = {}
        tool_names = ["Nmap", "SQLmap", "Nuclei", "Nikto", "Gobuster", "Dirsearch", "Commix", "Metasploit", "Netcat"]
        tool_keys  = ["Nmap", "Sqlmap", "Nuclei", "Nikto", "Gobuster", "Dirsearch", "Commix", "Metasploit", "Netcat"]

        tool_nav_row = ft.Row(spacing=5)
        for display_name, key in zip(tool_names, tool_keys):
            btn = ft.TextButton(
                display_name,
                on_click=lambda _, k=key: self.switch_tool(k),
                style=ft.ButtonStyle(color="white")
            )
            self.tool_buttons[key] = btn
            tool_nav_row.controls.append(btn)

        dvwa_link = ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color="amber", size=14),
            ft.Text("Alvo de Teste (DVWA):", size=12, color="blueGrey200"),
            ft.Text("", size=12, color="blue400", weight="bold", 
                    spans=[ft.TextSpan(" http://localhost:8081", url="http://localhost:8081")]),
            ft.Text("(Usuário: admin | Senha: password)", size=11, color="blueGrey400", italic=True)
        ], spacing=5)

        self.tab_header = ft.Container(
            content=ft.Row([
                tool_nav_row,
                ft.Column([
                    ft.Text("Pentester Suite — Ultimate Edition", size=14, weight="bold", color="blueGrey200"),
                    dvwa_link
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ft.Column([
                    services_panel,
                    ft.Row([self.status_text, self.loader], spacing=10),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=5),
            bgcolor=THEME_CARD,
            border=ft.border.only(bottom=ft.border.BorderSide(1, THEME_BORDER))
        )

        # Ferramentas
        self.nmap_tab = NmapTab(self, "Nmap")
        self.sqlmap_tab = SqlmapTab(self, "Sqlmap")
        self.nuclei_tab = NucleiTab(self, "Nuclei")
        self.nikto_tab = NiktoTab(self, "Nikto")
        self.gobuster_tab = GobusterTab(self, "Gobuster")
        self.dirsearch_tab = DirsearchTab(self, "Dirsearch")
        self.commix_tab = CommixTab(self, "Commix")
        self.netcat_tab = NetcatTab(self, "Netcat")
        self.metasploit_tab = MetasploitTab(self, "Metasploit")

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
        self.content_area = ft.Container(content=self.nmap_tab.view, expand=True)

        self.page.add(
            ft.Column([
                self.tab_header,
                self.content_area
            ], expand=True, spacing=0)
        )

        # Sobe o Docker
        self.set_loading("Iniciando Infraestrutura Docker...", True)
        try:
            try: subprocess.Popen(["docker-compose", "up", "-d"], cwd=DOCKER_DIR)
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

    async def _monitor_services(self):
        """Verifica o status dos containers e da API a cada 10 segundos."""
        while self._monitoring:
            try:
                # Checar containers Docker
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}"],
                    capture_output=True, text=True, timeout=5
                )
                running = result.stdout.lower() if result.returncode == 0 else ""
                
                self.svc_pentester.color = "green" if "pentester" in running else "red"
                self.svc_dvwa.color = "green" if "dvwa" in running else "red"
                self.svc_metasploit.color = "green" if "metasploit" in running else "red"
                
                # Checar Groq API (verifica se a chave existe)
                groq_key = os.getenv("GROQ_API_KEY", "")
                self.svc_groq.color = "green" if groq_key else "red"

                self.svc_pentester.update()
                self.svc_dvwa.update()
                self.svc_groq.update()
            except:
                pass
            
            await asyncio.sleep(10)

    def switch_tool(self, tool_name):
        if tool_name in self.tools:
            self.content_area.content = self.tools[tool_name].view
            self.content_area.update()

    def set_loading(self, status, visible=True):
        self.status_text.value = status
        self.loader.visible = visible
        self.status_text.update()
        self.loader.update()

    async def run_docker(self, container, cmd, on_output, tab=None):
        self.set_loading("Scanner em execução...")
        await run_docker(tab or self, container, cmd, on_output)
        self.set_loading("", False)

    def cancel_process(self, on_output=None, tab=None):
        cancel_process(tab or self, on_output)
        self.set_loading("Interrompido", False)
