import flet as ft
import os
import asyncio
import subprocess
from ui.nmap_tab import NmapTab
from ui.sqlmap_tab import SqlmapTab
from services.docker_runner import run_docker, cancel_process

class PentesterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Pentester Suite — Ultimate Edition"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#020617"
        self.page.padding = 0
        try: self.page.window_maximized = True
        except: pass
        
        self.page.fonts = {
            "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
        }
        
        self.report_findings = []
        self.tools = {}
        self._monitoring = True

    async def initialize(self):
        # Loader e Status
        self.loader = ft.ProgressBar(width=200, color="amber", visible=False)
        self.status_text = ft.Text("", size=11, italic=True, color="amber")

        # Indicadores de Serviços
        self.svc_pentester = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_dvwa = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_groq = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)

        services_panel = ft.Row([
            ft.Row([self.svc_pentester, ft.Text("Pentester", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_dvwa, ft.Text("DVWA", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_groq, ft.Text("Groq API", size=10, color="blueGrey300")], spacing=4),
        ], spacing=15)

        self.tab_header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.TextButton("Nmap", on_click=lambda _: self.switch_tool("Nmap"), style=ft.ButtonStyle(color="white")),
                    ft.TextButton("SQLmap", on_click=lambda _: self.switch_tool("Sqlmap"), style=ft.ButtonStyle(color="white")),
                ], spacing=10),
                ft.Text("Pentester Suite — Ultimate Edition", size=14, weight="bold", color="blueGrey200"),
                ft.Column([
                    services_panel,
                    ft.Row([self.status_text, self.loader], spacing=10),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=5),
            bgcolor="#0F172A",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#1E293B"))
        )

        # Ferramentas
        self.nmap_tab = NmapTab(self, "Nmap")
        self.sqlmap_tab = SqlmapTab(self, "Sqlmap")
        self.tools = {"Nmap": self.nmap_tab, "Sqlmap": self.sqlmap_tab}
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
            docker_path = os.path.join(os.getcwd(), "app", "docker")
            try: subprocess.Popen(["docker-compose", "up", "-d"], cwd=docker_path)
            except: subprocess.Popen(["docker", "compose", "up", "-d"], cwd=docker_path)
            await asyncio.sleep(2)
        except: pass
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

    async def run_docker(self, container, cmd, on_output):
        self.set_loading("Scanner em execução...")
        await run_docker(self, container, cmd, on_output)
        self.set_loading("", False)

    def cancel_process(self, on_output=None):
        cancel_process(on_output)
        self.set_loading("Interrompido", False)
