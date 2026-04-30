import flet as ft
from ui.tool_tab import ToolTab
from config import INPUT_STYLE
from tools.nikto import Nikto


class NiktoTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Avaliação Web / Servidor",
            "https://cirt.net/Nikto2",
            ft.Icons.LANGUAGE,
            ft.Icons.WEB,
            description="O Nikto é um scanner de servidores web. Ele executa testes extensivos buscando por milhares de arquivos e programas perigosos, versões desatualizadas de softwares e problemas de configuração.",
            help_text="""GUIA TÉCNICO NIKTO:

Scanner focado na segurança do servidor web e arquivos de configuração.

1. EXPLICAÇÃO DOS CAMPOS:
   - HOST/IP (-h): O endereço do servidor web alvo.
   - SSL: Se marcado, força o uso da flag '-ssl'. Use quando o alvo for HTTPS.
   - TUNING (-Tuning): 
     * 1: Injeção SQL.
     * 4: XSS.
     * 9: Command Injection.
     * g: Busca por 'Garbage' (arquivos temporários, backups, configs antigas).
   - USER AGENT: Define como o Nikto se identifica. Útil para contornar bloqueios simples que barram a palavra 'Nikto' no tráfego.

2. EXEMPLOS DE COMANDO GERADO:
   - Scan Padrão: nikto -h http://dvwa
   - Scan HTTPS com Tuning de XSS: nikto -h https://dvwa -ssl -Tuning 4
   - Scan com Identidade Falsa: nikto -h http://dvwa -useragent "Mozilla/5.0"

3. DICA: 
   O Nikto é excelente para encontrar falhas de 'Security Misconfiguration', como headers de segurança ausentes ou métodos HTTP perigosos habilitados.
   
4. ENTENDENDO A URL E PARÂMETROS:
   No Nikto, passamos o HOST (ex: `http://dvwa`). Se você colocar uma URL com parâmetros (ex: `index.php?id=1`), o Nikto focará no servidor que hospeda essa URL. Lembre-se: o `?` separa a página dos dados (parâmetros) e o `&` permite enviar várias informações de uma vez. O Nikto usa essas informações para entender o comportamento do servidor web."""
        )
        self.nikto = Nikto()

        input_style = INPUT_STYLE

        # Controles
        self.host = ft.TextField(
            label="Host / URL",
            value="http://dvwa",
            **input_style
        )

        self.port = ft.TextField(
            label="Porta (opcional)",
            value="",
            **input_style
        )

        self.ssl_switch = ft.Switch(
            label="Forçar SSL/HTTPS (-ssl)",
            value=False,
            active_color=ft.Colors.AMBER_400
        )

        self.tuning = ft.TextField(
            label="Tuning (ex: 123b)",
            value="",
            **input_style
        )

        self.plugins = ft.TextField(
            label="Plugins (ex: apacheusers)",
            value="",
            **input_style
        )

        self.user_agent = ft.TextField(
            label="User-Agent customizado",
            value="",
            **input_style
        )

        self.json_switch = ft.Switch(
            label="Gerar saída JSON",
            value=False,
            active_color=ft.Colors.TEAL_400
        )

        self.extra_params = ft.TextField(
            label="Parâmetros extras",
            value="",
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.host,
            self.port,
            self.ssl_switch,
            self.tuning,
            self.plugins,
            self.user_agent,
            self.json_switch,
            self.extra_params,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.host.value = "dvwa"
        self.port.value = ""
        self.ssl_switch.value = False
        self.tuning.value = ""
        self.plugins.value = ""
        self.user_agent.value = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Vaporeon"
        self.json_switch.value = True
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
                cmd_list = [self.nikto.binary] + shlex.split(self.raw_cmd.value)
            else:
                cmd_list = self.nikto.build_command(
                    host=self.host.value,
                    port=self.port.value,
                    ssl_switch=self.ssl_switch.value,
                    tuning=self.tuning.value,
                    plugins=self.plugins.value,
                    user_agent=self.user_agent.value,
                    json_switch=self.json_switch.value,
                    extra_params=self.extra_params.value
                )
            self.last_command = self.nikto.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.nikto.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
