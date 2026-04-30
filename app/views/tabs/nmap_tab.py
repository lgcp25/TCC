import flet as ft
from views.tool_tab import ToolTab
from models.nmap import Nmap
from config import INPUT_STYLE, THEME_BORDER
import datetime
import shlex

class NmapTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app, 
            name, 
            "Reconhecimento / Mapeamento de Rede", 
            "https://nmap.org/book/man.html",
            ft.Icons.NETWORK_CHECK,
            ft.Icons.NETWORK_CELL,
            description="O Nmap é o Scanner de Segurança mais popular do mundo. Ele vasculha IPs, descobre portas abertas, detecta serviços rodando e identifica o sistema operacional do alvo.",
            help_text="""GUIA TÉCNICO NMAP (Network Mapper):

Esta interface abstrai as flags mais poderosas do Nmap para facilitar o uso acadêmico.

1. EXPLICAÇÃO DOS CAMPOS:
   - ALVO: Endereço IP (192.168.1.1), rede (192.168.1.0/24) ou domínio (alvo.com).
   - PERFIL: 
     * Scan Rápido: Usa a flag '-F', escaneando apenas as 100 portas mais comuns.
     * Scan de Serviço: Usa '-sV', enviando pacotes específicos para cada porta aberta para determinar a versão do software.
     * Scan de SO: Usa '-O', analisando a latência e janelas TCP para 'adivinhar' o sistema operacional.
     * Scan Completo: Usa '-A' (Aggressive), que habilita detecção de SO, versão, scripts padrão e traceroute.
   - ESPECIFICAR PORTAS: Habilita a flag '-p'. Se desativado, o Nmap escaneia as 1000 portas mais comuns por padrão.
   - TIMING (Velocidade): Controla o delay entre pacotes ('-T0' a '-T5'). Recomendamos T4 para equilíbrio entre velocidade e precisão.
   - SCRIPT SCAN: Habilita '--script=vuln', invocando o motor NSE (Nmap Scripting Engine) para buscar falhas conhecidas como CVEs.

2. EXEMPLOS DE COMANDO GERADO:
   - Básico: nmap -T4 192.168.1.1
   - Com Versão e SO: nmap -sV -O -T4 192.168.1.1
   - Busca de Vulnerabilidades: nmap -sV --script=vuln -T4 192.168.1.1

3. DICA: 
   O Nmap é o padrão ouro na fase de 'Footprinting'. Identificar a versão correta de um serviço é o primeiro passo para encontrar um exploit público no Exploit-DB."""
        )
        self.nmap = Nmap()

        input_style = INPUT_STYLE

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
            self.raw_cmd.value = ""
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

        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.scan_profile,
            ft.Row([self.port_switch], alignment=ft.MainAxisAlignment.START),
            self.port,
            self.timing,
            self.script_scan,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "dvwa"
        self.target.disabled = False
        self.port_switch.value = False
        self.port_switch.disabled = False
        self.port.value = ""
        self.port.disabled = True
        self.scan_profile.value = "Scan portas comuns (top 1000)"
        self.scan_profile.disabled = False
        self.timing.disabled = False
        self.script_scan.value = "default"
        self.script_scan.disabled = False
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    def get_command(self):
        if self.free_cmd_switch.value:
            return f"nmap {self.raw_cmd.value}"

        timing_map = {
            "T0 (Paranóico - Evasão Extrema)": "-T0",
            "T1 (Furtivo - Lento)": "-T1",
            "T2 (Polido)": "-T2",
            "T3 (Normal)": "-T3",
            "T4 (Agressivo - Recomendado)": "-T4",
            "T5 (Insano - Redes Locais)": "-T5"
        }
        script_val = self.script_scan.value.split(" ")[0]
        
        cmd = self.nmap.build_command(
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
            if self.free_cmd_switch.value:
                cmd_str = self.raw_cmd.value
                self.last_command = f"nmap {cmd_str}"
                await self.write_terminal(f"[COMANDO] nmap {cmd_str}\n\n")
                cmd_list = ["nmap"] + shlex.split(cmd_str)
            else:
                cmd_str = self.get_command()
                self.last_command = cmd_str
                await self.write_terminal(f"[COMANDO] {cmd_str}\n\n")
                cmd_list = shlex.split(cmd_str)
            
            await self.app.run_docker("pentester", cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
