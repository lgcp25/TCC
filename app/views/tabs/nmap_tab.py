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
            help_text="""GUIA TÉCNICO COMPLETO DO NMAP (Network Mapper):

╔══════════════════════════════════════════════════════════════╗
║                        NMAP - AJUDA                         ║
╚══════════════════════════════════════════════════════════════╝

O Nmap é o scanner de segurança mais popular do mundo.

FUNÇÕES PRINCIPAIS:
 • Descobrir hosts ativos
 • Encontrar portas abertas
 • Identificar serviços
 • Detectar versões de softwares
 • Identificar sistemas operacionais
 • Executar scripts NSE

═══════════════════════════════════════════════════════════════
[1] IP OU DOMÍNIO
═══════════════════════════════════════════════════════════════

O alvo que será analisado.

Exemplos:
 • 192.168.1.10
 • scanme.nmap.org
 • exemplo.com

═══════════════════════════════════════════════════════════════
[2] OBJETIVO DO SCAN
═══════════════════════════════════════════════════════════════

[01] Scan Rápido
     • Escaneia as 1000 portas mais comuns.
     • Ideal para reconhecimento inicial.

[02] Varredura Profunda
     • Descobre versões dos serviços.
     • Detecta sistema operacional.
     • Mais lenta, porém mais completa.

[03] Scan Agressivo
     • Detecta SO.
     • Detecta versões.
     • Executa scripts.
     • Realiza traceroute.
     • Produz muito tráfego.

[04] Mapear Todas as Portas
     • Escaneia da porta 1 até 65535.
     • Encontra serviços em portas incomuns.

[05] Investigar Porta Específica
     • Analisa apenas uma porta.
     • Permite uso de Scripts NSE.

[06] Scan UDP
     • Procura serviços UDP.
     • Ex.: DNS, SNMP, NTP.

[07] Descobrir Hosts Ativos
     • Mostra quais máquinas estão online.

[08] Detectar Sistema Operacional
     • Tenta identificar o SO do alvo.

[09] Identificar Versões dos Serviços
     • Exibe versões de softwares encontrados.

[10] Scan SYN
     • Rápido e eficiente.
     • Menos barulhento.

[11] Scripts NSE Seguros
     • Executa scripts não intrusivos.

[12] Analisar Servidor Web
     • Focado em HTTP e HTTPS.

[13] Verificar Certificado SSL/TLS
     • Analisa certificados HTTPS.

[14] Descobrir Compartilhamentos SMB
     • Lista compartilhamentos Windows.

[15] Enumerar Usuários SMB
     • Procura usuários expostos.

[16] Detectar Serviços Comuns
     • Varredura rápida dos serviços mais usados.

[17] Scan Web Completo
     • Portas 80, 443, 8080 e 8443.

[18] Scan com Resolução DNS
     • Resolve nomes associados aos IPs.

[19] Descobrir Hosts e Serviços Básicos
     • Reconhecimento geral da rede.

[20] Scan Balanceado
     • Melhor opção para iniciantes.
     • Equilíbrio entre velocidade e detalhes.

═══════════════════════════════════════════════════════════════
[3] SCRIPTS NSE
═══════════════════════════════════════════════════════════════

Disponível apenas em:

 ► [05] Investigar Porta Específica

Categorias:

 • default    -> Coleta informações básicas
 • safe       -> Scripts seguros
 • vuln       -> Busca vulnerabilidades conhecidas
 • discovery  -> Enumeração avançada
 • auth       -> Análise de autenticação
 • brute      -> Testes de credenciais
 • exploit    -> Validação de vulnerabilidades

═══════════════════════════════════════════════════════════════
[DICA DE OURO]
═══════════════════════════════════════════════════════════════

O segredo do pentest não é explorar primeiro.

Primeiro descubra:
 • Quais portas estão abertas
 • Quais serviços estão rodando
 • Quais versões estão instaladas

Quanto melhor a enumeração, maior a chance de encontrar
vulnerabilidades reais posteriormente."""
        )
        self.nmap = Nmap()

        input_style = INPUT_STYLE

        self.target = ft.TextField(label="Alvo (URL ou IP)", value="http://dvwa", **input_style)
        self.port = ft.TextField(label="Portas (Desativado)", value="", disabled=True, **input_style)

                  
        # Comando Manual (Igual à porta)
        self.free_cmd_field = ft.TextField(
            label="Digite o comando completo (ex: nmap -A alvo)",
            value="nmap ",
            disabled=True,
            **input_style,
            focused_border_color=ft.Colors.PURPLE_400
        )



        self.scan_profile = ft.Dropdown(
            label="Objetivo do Scan (O que você quer descobrir?)",
            on_select=self.enable_port,
            options=[
                ft.dropdown.Option("1. Scan Rápido (Top 1000 portas)"),
                ft.dropdown.Option("2. Varredura Profunda (Lento, mas com bom retorno)"),
                ft.dropdown.Option("3. Scan Agressivo (Barulhento, traz muitos dados)"),
                ft.dropdown.Option("4. Mapear Todas as Portas (1 a 65535)"),
                ft.dropdown.Option("5. Investigar Porta Específica"),
                ft.dropdown.Option("6. Scan de Portas UDP (Mais lento)"),
                ft.dropdown.Option("7. Descobrir Hosts Ativos na Rede"),
                ft.dropdown.Option("8. Detectar Sistema Operacional"),
                ft.dropdown.Option("9. Identificar Versões dos Serviços"),
                ft.dropdown.Option("10. Scan SYN (Rápido e Eficiente)"),
                ft.dropdown.Option("11. Executar Scripts NSE Seguros"),
                ft.dropdown.Option("12. Analisar Servidor Web (HTTP/HTTPS)"),
                ft.dropdown.Option("13. Verificar Certificado SSL/TLS"),
                ft.dropdown.Option("14. Descobrir Compartilhamentos SMB"),
                ft.dropdown.Option("15. Enumerar Usuários SMB"),
                ft.dropdown.Option("16. Detectar Serviços Comuns (Fast Scan)"),
                ft.dropdown.Option("17. Scan Web Completo (80,443,8080,8443)"),
                ft.dropdown.Option("18. Scan com Resolução DNS"),
                ft.dropdown.Option("19. Descobrir Hosts e Serviços Básicos"),
                ft.dropdown.Option("20. Scan Balanceado (Recomendado para Iniciantes)"),
            ],
            value="1. Scan Rápido (Top 1000 portas)",
            **input_style
        )

        self.script_scan = ft.Dropdown(
            label="Script Scan (NSE)",
            disabled=True,
            value="",
            options=[
                ft.dropdown.Option("default (Script padrão)"),
                ft.dropdown.Option("vuln (Vulnerabilidades)"),
                ft.dropdown.Option("safe (Seguro/Não Intrusivo)"),
                ft.dropdown.Option("brute (Força Bruta)"),
                ft.dropdown.Option("auth (Autenticação)"),
                ft.dropdown.Option("discovery (Descoberta)"),
                ft.dropdown.Option("exploit (Exploração)")
            ],
            **input_style
        )

        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.scan_profile,
            self.port,
            self.script_scan,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "dvwa"
        self.target.disabled = False
        self.port.value = ""
        self.port.disabled = True
        self.scan_profile.value = "1. Scan Rápido (Top 1000 portas)"
        self.scan_profile.disabled = False
        self.script_scan.value = "default"
        self.script_scan.disabled = True
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()
        
    def get_command(self):
        if self.free_cmd_switch.value:
            return self.raw_cmd.value
            
        cmd = self.nmap.build_command(
            target=self.target.value,
            mode=self.scan_profile.value,
            port=self.port.value,
            os_detect=False,
            script_scan=self.script_scan.value,
            verbose=False
        )
        return self.nmap.pretty_command(cmd)

    async def enable_port(self, e):
            if self.scan_profile.value == "5. Investigar Porta Específica":
                self.port.disabled = False  
                self.port.label = "Portas (Digite aqui)" if not self.port.disabled else "Portas (Desativado)"
                self.script_scan.disabled = False  
                self.script_scan.label = "Script Scan (NSE)" if not self.script_scan.disabled else "Script não aplicavél"
            else:
                self.port.label = "Portas (Desativado)"
                self.port.value = ""
                self.port.disabled = True
                self.script_scan.label = "Script não aplicavél"
                self.script_scan.value = ""
                self.script_scan.disabled = True
            self.left_col.update()
            
    async def run(self, e):
        await self.clear_terminal()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        try:
            if self.free_cmd_switch.value:
                cmd_str = self.raw_cmd.value
                self.last_command = cmd_str
                await self.write_terminal(f"[COMANDO] {cmd_str}\n\n")
                cmd_list = shlex.split(cmd_str)
            else:
                cmd_str = self.get_command()
                self.last_command = cmd_str
                await self.write_terminal(f"[COMANDO] {cmd_str}\n\n")
                cmd_list = shlex.split(cmd_str)
            
            await self.app.run_docker("pentester", cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
