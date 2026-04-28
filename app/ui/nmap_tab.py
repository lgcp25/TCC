import flet as ft
from ui.tool_tab import ToolTab
from tools.nmap import Nmap
import datetime

class NmapTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app, 
            name, 
            "Reconhecimento / Varredura", 
            "https://nmap.org/book/man.html",
            ft.Icons.SEARCH,
            ft.Icons.RADAR
        )
        self.nmap = Nmap()

        input_style = dict(
            border_color="transparent", 
            filled=True, 
            bgcolor="#1F2937", 
            text_size=12, 
            label_style=ft.TextStyle(size=12, color=ft.Colors.BLUE_GREY_400), 
            content_padding=10, 
            height=40
        )

        # Controles
        self.target = ft.TextField(label="IP ou domínio", value="dvwa", **input_style)
        self.port_switch = ft.Switch(label="Usar Porta Específica?", value=False, active_color=ft.Colors.BLUE_400)
        self.port = ft.TextField(label="Portas (Desativado)", value="", disabled=True, **input_style)

        def toggle_port(e):
            self.port.disabled = not self.port_switch.value
            self.port.label = "Portas (Digite aqui)" if not self.port.disabled else "Portas (Desativado)"
            if self.port.disabled:
                self.port.value = ""
            self.port.update()
            self.app.page.update()

        self.port_switch.on_change = toggle_port

        # Comando Manual (Igual à porta)
        self.free_cmd_field = ft.TextField(
            label="Digite o comando completo (ex: nmap -A alvo)",
            value="nmap ",
            disabled=True,
            **input_style,
            focused_border_color=ft.Colors.PURPLE_400
        )



        self.free_cmd_switch = ft.Switch(
            label="Comando Manual", 
            value=False, 
            active_color=ft.Colors.PURPLE_400,
            disabled=False
        )

        def toggle_free_mode(e):
            self.target.disabled = self.free_cmd_switch.value
            self.port_switch.disabled = self.free_cmd_switch.value
            self.port.disabled = self.free_cmd_switch.value or not self.port_switch.value
            self.scan_profile.disabled = self.free_cmd_switch.value
            self.timing.disabled = self.free_cmd_switch.value
            self.script_scan.disabled = self.free_cmd_switch.value
            self.free_cmd_field.disabled = not self.free_cmd_switch.value
            self.free_cmd_field.update()
            self.app.page.update()

        self.free_cmd_switch.on_change = toggle_free_mode

        self.scan_profile = ft.Dropdown(
            label="Perfil de Scan",
            options=[
                ft.dropdown.Option("Ver portas abertas (varre todas as portas, pode demorar)"),
                ft.dropdown.Option("Scan portas comuns (top 1000)"),
                ft.dropdown.Option("Scan porta específica (usar campo Porta)"),
                ft.dropdown.Option("Varredura completa TCP com detecção de SO e versões (-p- -sS -sV -O)"),
                ft.dropdown.Option("Scan agressivo (scripts default + OS + version) (-A)"),
                ft.dropdown.Option("UDP scan (top 1000) (-sU)"),
                ft.dropdown.Option("Usar scripts de vulnerabilidade (--script vuln)")
            ],
            value="Scan portas comuns (top 1000)",
            **input_style
        )
        
        self.timing = ft.Dropdown(
            label="Timing Template (Velocidade)",
            options=[
                ft.dropdown.Option("T0 (Paranóico - Evasão Extrema)"),
                ft.dropdown.Option("T1 (Furtivo - Lento)"),
                ft.dropdown.Option("T2 (Polido)"),
                ft.dropdown.Option("T3 (Normal)"),
                ft.dropdown.Option("T4 (Agressivo - Recomendado)"),
                ft.dropdown.Option("T5 (Insano - Redes Locais)")
            ],
            value="T4 (Agressivo - Recomendado)",
            **input_style
        )

        self.script_scan = ft.Dropdown(
            label="Script Scan (NSE)",
            options=[
                ft.dropdown.Option("default"),
                ft.dropdown.Option("vuln (Vulnerabilidades)"),
                ft.dropdown.Option("safe (Seguro/Não Intrusivo)"),
                ft.dropdown.Option("brute (Força Bruta)"),
                ft.dropdown.Option("auth (Autenticação)"),
                ft.dropdown.Option("discovery (Descoberta)"),
                ft.dropdown.Option("exploit (Exploração)")
            ],
            value="default",
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.scan_profile,
            ft.Row([self.port_switch], alignment=ft.MainAxisAlignment.START),
            self.port,
            self.timing,
            self.script_scan,
            self.free_cmd_switch,
            self.free_cmd_field
        ])

    def reset_fields(self):
        self.target.value = "dvwa"
        self.target.disabled = False
        self.port_switch.value = False
        self.port_switch.disabled = False
        self.port.value = ""
        self.port.disabled = True
        self.scan_profile.value = "Scan portas comuns (top 1000)"
        self.scan_profile.disabled = False
        self.timing.value = "T4 (Agressivo - Recomendado)"
        self.timing.disabled = False
        self.script_scan.value = "default"
        self.script_scan.disabled = False
        self.free_cmd_switch.value = False
        self.free_cmd_field.value = "nmap "
        self.free_cmd_field.disabled = True
        self.app.page.update()

    def get_command(self):
        if self.free_cmd_switch.value:
            return self.free_cmd_field.value.strip()

        timing_map = {
            "T0 (Paranóico - Evasão Extrema)": "-T0",
            "T1 (Furtivo - Lento)": "-T1",
            "T2 (Polido)": "-T2",
            "T3 (Normal)": "-T3",
            "T4 (Agressivo - Recomendado)": "-T4",
            "T5 (Insano - Redes Locais)": "-T5"
        }
        script_val = self.script_scan.value.split(" ")[0]
        
        cmd = self.nmap.build_nmap_command(
            target=self.target.value,
            mode=self.scan_profile.value,
            port=self.port.value if self.port_switch.value else None,
            timing=timing_map.get(self.timing.value, "-T4"),
            os_detect=False,
            script_scan=script_val,
            verbose=False
        )
        return self.nmap.pretty_command(cmd)

    async def run(self, e):
        await self.clear_terminal()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        await self.write_terminal(f"Starting Nmap 7.94 ( https://nmap.org ) at {now} -03\n")
        
        try:
            cmd_str = self.get_command()
            self.last_command = cmd_str
            await self.write_terminal(f"[COMANDO] {cmd_str}\n\n")
            cmd_list = cmd_str.split(" ")
            await self.app.run_docker("pentester", cmd_list, on_output=self.write_terminal)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
