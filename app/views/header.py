import flet as ft
import asyncio
from config import THEME_CARD, THEME_BORDER

class HeaderPanel(ft.Container):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.loader = ft.ProgressBar(width=200, color="amber", visible=False)
        self.status_text = ft.Text("", size=11, italic=True, color="amber")

        self.svc_pentester = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_dvwa = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)
        self.svc_groq = ft.Icon(ft.Icons.CIRCLE, color="red", size=10)

        services_panel = ft.Row([
            ft.Row([self.svc_pentester, ft.Text("Pentester", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_dvwa, ft.Text("DVWA", size=10, color="blueGrey300")], spacing=4),
            ft.Row([self.svc_groq, ft.Text("Groq API", size=10, color="blueGrey300")], spacing=4),
        ], spacing=15)
        
        
        self.reset_enviroment = ft.OutlinedButton(
            "Reset Lab",
            icon=ft.Icons.RESTART_ALT,
            on_click=self.on_reset_environment,
            height=28,
            margin=ft.margin.only(top=2)
        )

        self.controller.tool_buttons = {}
        tool_names = ["Nmap", "Gobuster", "Nikto", "SQLmap", "Netcat"]
        tool_keys  = ["Nmap", "Gobuster", "Nikto", "Sqlmap", "Netcat"]

        tool_nav_row = ft.Row(spacing=5)
        for display_name, key in zip(tool_names, tool_keys):
            btn = ft.TextButton(
                display_name,
                on_click=lambda _, k=key: self.controller.switch_tool(k),
                style=ft.ButtonStyle(color="white")
            )
            self.controller.tool_buttons[key] = btn
            tool_nav_row.controls.append(btn)

        dvwa_link = ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color="amber", size=14),
            ft.Text("Alvo de Teste (DVWA):", size=12, color="blueGrey200"),
            ft.Text("", size=12, color="blue400", weight="bold", 
                    spans=[ft.TextSpan(" http://localhost:8081", url="http://localhost:8081")]),
            ft.Text("(Usuário: admin | Senha: password)", size=11, color="blueGrey400", italic=True)
        ], spacing=5)

        self.content = ft.Row([
            tool_nav_row,
            ft.Column([
                ft.Text("Vaporeon - Pentester Suite", size=14, weight="bold", color="blueGrey200"),
                dvwa_link
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            ft.Column([
                services_panel,
                self.reset_enviroment,
                ft.Row([self.status_text, self.loader], spacing=10),
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.padding = ft.padding.symmetric(horizontal=20, vertical=5)
        self.bgcolor = THEME_CARD
        self.border = ft.border.only(bottom=ft.border.BorderSide(1, THEME_BORDER))
        
    def on_reset_environment(self, e):
        asyncio.ensure_future(
            self.controller.reset_env()
        )
