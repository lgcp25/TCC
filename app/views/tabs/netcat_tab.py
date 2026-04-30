import flet as ft
from views.tool_tab import ToolTab
from config import INPUT_STYLE
from models.netcat import Netcat


class NetcatTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Conexões de Rede / Pós-Exploração",
            "https://nc110.sourceforge.io/",
            ft.Icons.CABLE,
            ft.Icons.SENSORS,
            description="O Netcat é o 'Canivete Suíço' das redes. Ele pode ler e escrever dados através de conexões de rede TCP/UDP. É vital na Pós-Exploração para escutar ou receber Reverse Shells.",
            help_text="""GUIA TÉCNICO NETCAT (NC):

A ferramenta mais versátil para conexões de rede diretas e arbitrárias.

1. EXPLICAÇÃO DOS CAMPOS:
   - MODO LISTENER (-l -p): Abre uma porta no SEU computador. Você fica esperando o alvo se conectar a você (técnica de Reverse Shell).
   - MODO CLIENTE: Você se conecta a uma porta aberta no alvo (Bind Shell ou teste de porta).
   - HOST/PORTA: O endereço e a porta para a comunicação.
   - ARQUIVO: Permite ler o conteúdo de um arquivo e enviá-lo pelo túnel do Netcat ou salvar o que for recebido.

2. EXEMPLOS DE COMANDO GERADO:
   - Abrir Ouvinte na porta 4444: nc -lvp 4444
   - Conectar a um Servidor Web: nc 192.168.1.1 80
   - Receber um arquivo: nc -lvp 4444 > recebido.txt

3. DICA: 
   O Netcat é a base do 'Exfiltração de Dados'. Ele é simples, leve e está presente em quase todos os sistemas Linux por padrão, tornando-o uma ferramenta furtiva e poderosa."""
        )
        self.netcat = Netcat()

        input_style = INPUT_STYLE

        # Controles
        self.mode = ft.Dropdown(
            label="Modo de Operação",
            value="Conectar (cliente)",
            options=[
                ft.dropdown.Option("Conectar (cliente)"),
                ft.dropdown.Option("Escutar (servidor)"),
                ft.dropdown.Option("Banner Grab"),
                ft.dropdown.Option("Enviar arquivo"),
                ft.dropdown.Option("Receber arquivo"),
                ft.dropdown.Option("Raw Command (avançado)"),
            ],
            **input_style
        )

        self.host = ft.TextField(
            label="Host (IP / domínio)",
            value="",
            **input_style
        )

        self.port = ft.TextField(
            label="Porta",
            value="4444",
            **input_style
        )

        self.file_path = ft.TextField(
            label="Arquivo (para transferência)",
            value="",
            **input_style
        )

        self.raw_cmd = ft.TextField(
            label="Raw Netcat Command",
            value="",
            **input_style
        )

        self.extra_params = ft.TextField(
            label="Parâmetros extras",
            value="",
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.mode,
            self.host,
            self.port,
            self.file_path,
            self.extra_params,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.mode.value = "Conectar (cliente)"
        self.host.value = ""
        self.port.value = ""
        self.file_path.value = ""
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
                cmd_list = [self.netcat.binary] + shlex.split(self.raw_cmd.value)
            else:
                cmd_list = self.netcat.build_command(
                    mode=self.mode.value,
                    host=self.host.value,
                    port=self.port.value,
                    file_path=self.file_path.value,
                    raw_cmd="", # O campo raw_cmd antigo não é mais usado desta forma
                    extra_params=self.extra_params.value
                )
            self.last_command = self.netcat.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.netcat.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
