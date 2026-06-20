import flet as ft
import os
import asyncio
import subprocess
import logging
from controllers.nmap_controller import NmapController
from controllers.gobuster_controller import GobusterController
from controllers.nikto_controller import NiktoController
from controllers.sqlmap_controller import SqlmapController
from controllers.netcat_controller import NetcatController
from controllers.ai_controller import AiController
from controllers.report_controller import ReportController
from config import THEME_BG, THEME_CARD, THEME_BORDER, DOCKER_DIR
from views.tabs import (
    NmapTab, GobusterTab, NiktoTab, SqlmapTab, NetcatTab
)
from services.tool_executor import ToolExecutor


logger = logging.getLogger(__name__)

class MainController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.executor = ToolExecutor()
        
        self.report_findings = []
        self.tools = {}
        self.monitoring = True
        self.active_tool = None
        self.dvwa_cookies = {}
        
    async def initialize(self):        
        from views.header import HeaderPanel
        
        self.tab_header = HeaderPanel(self)
        
        self.ai_controller = AiController(self)
        self.report_controller = ReportController(self)
        
        self.nmap_controller = NmapController(self)
        self.nmap_tab = NmapTab(self,"Nmap", self.nmap_controller)
        
        self.gobuster_controller = GobusterController(self)
        self.gobuster_tab = GobusterTab(self,"Gobuster", self.gobuster_controller)
        
        self.nikto_controller = NiktoController(self)
        self.nikto_tab = NiktoTab(self,"Nikto",self.nikto_controller)
        
        self.sqlmap_controller = SqlmapController(self)
        self.sqlmap_tab = SqlmapTab(self, "Sqlmap", self.sqlmap_controller)
        
        self.netcat_controller = NetcatController(self)
        self.netcat_tab = NetcatTab(self,"Netcat",self.netcat_controller)

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
            self.executor.initialize_docker()
            
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
                groq_ok = bool(os.getenv("GROQ_API_KEY", ""))

                # Delega ao HeaderPanel — controller não conhece widgets
                self.tab_header.set_service_status(
                    pentester="pentester" in running,
                    dvwa="dvwa" in running,
                    groq=groq_ok
                )
            except:
                pass
            await asyncio.sleep(10)
    
            
    def set_loading(self, status: str, visible: bool = True):
        self.tab_header.set_loading(status, visible)

    
        
    async def reset_env(self):
        self.set_loading("Restaurando ambiente...", True)
        self.tab_header.set_service_status(pentester=False, dvwa=False, groq=False)

        try:
            success = await self.executor.restart_docker()

            if not success:
                self.set_loading("", False)
                return

            # Aguarda mais tempo para os containers subirem completamente
            await asyncio.sleep(5)

            from services.dvwa_service import wait_and_init_dvwa

            cookies = await wait_and_init_dvwa()

            if cookies:
                self.dvwa_cookies = cookies
                logger.info(f"[reset_env] Cookies atualizados: {self.dvwa_cookies}")

        except Exception as e:
            logger.error(f"Erro ao restaurar ambiente: {e}")

        finally:
            self.set_loading("", False)
            # Re-aplica o destaque do botão ativo após o reinício
            if self.active_tool:
                self.switch_tool(self.active_tool)
            
    def switch_tool(self, tool_name):
        if tool_name in self.tools:
            self.content_area.content = self.tools[tool_name].view
            self.content_area.update()
            self.active_tool = tool_name
            # Delega o estilo visual dos botões ao HeaderPanel
            self.tab_header.set_active_tool(tool_name)

    def cancel(self, on_output=None, tab=None):
        self.executor.cancel_process(on_output)
        self.set_loading("Interrompido", False)
        if tab:
            tab.set_executing(False)
    
