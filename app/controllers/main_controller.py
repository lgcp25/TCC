import flet as ft
import os
import asyncio
import subprocess
import logging
import services.docker_runner as docker_runner
from config import THEME_BG, THEME_CARD, THEME_BORDER, DOCKER_DIR
from views.tabs import (
    NmapTab, GobusterTab, NiktoTab, SqlmapTab, NetcatTab
)
from services.docker_runner import run_docker_turbo, cancel_process


logger = logging.getLogger(__name__)

class PentesterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Vaporeon - Pentester Suite"
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
        self.monitoring = True
        self.active_tool = None
        self.dvwa_cookies = {}

    async def initialize(self):
        from views.header import HeaderPanel
        
        self.tab_header = HeaderPanel(self)
        self.nmap_tab = NmapTab(self, "Nmap")
        self.gobuster_tab = GobusterTab(self, "Gobuster")
        self.nikto_tab = NiktoTab(self, "Nikto")
        self.sqlmap_tab = SqlmapTab(self, "Sqlmap")
        self.netcat_tab = NetcatTab(self, "Netcat")

        self.tools = {
            "Nmap": self.nmap_tab,
            "Gobuster": self.gobuster_tab,
            "Nikto": self.nikto_tab,
            "Sqlmap": self.sqlmap_tab,
            "Netcat": self.netcat_tab,
        }
        self.content_area = ft.Container(content=self.nmap_tab.view, expand=True)

        self.page.add(
            ft.Column([
                self.tab_header,
                self.content_area
            ], expand=True, spacing=0)
        )
        
        self.set_loading("Iniciando Infraestrutura Docker...", True)

        try:
            docker_runner.docker_init()
            
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
        self.switch_tool("Nmap")
        asyncio.ensure_future(self.monitor_svc())

    async def monitor_svc(self):
        while self.monitoring:
            try:
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}"],
                    capture_output=True, text=True, timeout=5
                )
                running = result.stdout.lower() if result.returncode == 0 else ""
                
                self.tab_header.svc_pentester.color = "green" if "pentester" in running else "red"
                self.tab_header.svc_dvwa.color = "green" if "dvwa" in running else "red"
                groq_key = os.getenv("GROQ_API_KEY", "")
                self.tab_header.svc_groq.color = "green" if groq_key else "red"

                self.tab_header.svc_pentester.update()
                self.tab_header.svc_dvwa.update()
                self.tab_header.svc_groq.update()

            except:
                pass
            await asyncio.sleep(10)
    def switch_tool(self, tool_name):
        if tool_name in self.tools:
            self.content_area.content = self.tools[tool_name].view
            self.content_area.update()
            self.active_tool = tool_name

            if hasattr(self, 'tool_buttons'):
                for key, btn in self.tool_buttons.items():
                    if key == tool_name:
                        btn.style = ft.ButtonStyle(color="white", bgcolor="blue700")
                    else:
                        btn.style = ft.ButtonStyle(color="blueGrey300", bgcolor=ft.Colors.TRANSPARENT)
                    btn.update()


    def set_loading(self, status, visible=True):
        self.tab_header.status_text.value = status
        self.tab_header.loader.visible = visible
        self.tab_header.status_text.update()
        self.tab_header.loader.update()

    async def run_docker(self, container, cmd, on_output, tab=None):
        self.set_loading("Scanner em execução...")
        
        if container == "pentester":
            self.tab_header.svc_pentester.color = "green"
            self.tab_header.svc_pentester.update()
        
        def finish_callback():
            self.set_loading("", False)
            
            if tab and hasattr(tab, "terminal_output"):
                try:
                    tab.terminal_output.update()
                except:
                    pass
                
        docker_runner.run_docker_turbo(tab or self, container, cmd, on_output, on_finish=finish_callback)
        
    async def reset_env(self):
        self.set_loading("Restaurando ambiente...", True)
        self.tab_header.svc_pentester.color = "orange"
        self.tab_header.svc_dvwa.color = "orange"

        self.tab_header.svc_pentester.update()
        self.tab_header.svc_dvwa.update()

        try:
            success = await asyncio.to_thread(
                docker_runner.restart_environment
            )

            if not success:
                self.set_loading("", False)
                return

            await asyncio.sleep(3)

            from services.dvwa_service import wait_and_init_dvwa

            cookies = await wait_and_init_dvwa()

            if cookies:
                self.dvwa_cookies = cookies


        except Exception as e:
            logger.error(f"Erro ao restaurar ambiente: {e}")

        finally:
            self.set_loading("", False)
        
        

    def cancel_process(self, on_output=None, tab=None):
        cancel_process(tab or self, on_output)
        self.set_loading("Interrompido", False)
