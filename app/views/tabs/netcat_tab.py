import flet as ft
from views.tool_tab import ToolTab
from config import INPUT_STYLE
from models.netcat import Netcat


class NetcatTab(ToolTab):
    def __init__(self, app, name, controller):
        self.controller = controller
        super().__init__(
            app,
            name,
            "Conexões de Rede / Pós-Exploração",
            "https://nc110.sourceforge.io/",
            ft.Icons.CABLE,
            ft.Icons.SENSORS,
            description="O Netcat é o 'Canivete Suíço' das redes. Ele pode ler e escrever dados através de conexões de rede TCP/UDP. É vital na Pós-Exploração para escutar ou receber Reverse Shells.",
            help_text="""GUIA TÉCNICO COMPLETO DO NETCAT (NC):

╔══════════════════════════════════════════════════════════════╗
║                      NETCAT - AJUDA                         ║
╚══════════════════════════════════════════════════════════════╝

O Netcat (nc) é uma ferramenta de comunicação de rede.

Ele permite:

• Abrir conexões TCP e UDP
• Escutar portas locais
• Testar serviços remotos
• Capturar banners
• Transferir dados entre hosts
• Receber conexões de aplicações remotas

É conhecido como o "Canivete Suíço das Redes".

═══════════════════════════════════════════════════════════════
[1] MODO DE OPERAÇÃO
═══════════════════════════════════════════════════════════════

[CLIENTE]
Conectar a um Alvo (Bind Shell)

Seu computador inicia a conexão.

Fluxo:

Seu PC ─────► Alvo

Utilizado quando o serviço remoto já está
aceitando conexões.

Exemplos:

• Testar serviços TCP
• Conectar em portas abertas
• Acessar aplicações de rede

────────────────────────────────────────────

[SERVIDOR]
Ouvir Porta Local (Reverse Shell)

Seu computador fica aguardando conexões.

Fluxo:

Seu PC ◄───── Alvo

Muito utilizado em laboratórios para
receber conexões originadas por sistemas
remotos.

Exemplos:

• Receber conexões de teste
• Laboratórios de pós-exploração
• Simulações de acesso remoto

────────────────────────────────────────────

[BANNER GRABBING]
Testar Porta / Banner Grabbing

Conecta rapidamente ao serviço e tenta
capturar informações iniciais.

Pode revelar:

• Nome do serviço
• Versão
• Mensagens de boas-vindas
• Tecnologias utilizadas

Exemplos:

SSH:
OpenSSH_8.9

FTP:
vsFTPd 3.0.3

HTTP:
Apache/2.4.57

═══════════════════════════════════════════════
[2] ALVO
═══════════════════════════════════════════════

IP ou domínio do sistema remoto.

Exemplos:

• 192.168.1.10
• scanme.nmap.org
• empresa.local

IMPORTANTE:

No modo "Ouvir Porta Local"
este campo deve ficar vazio.

═══════════════════════════════════════════════
[3] PORTA
═══════════════════════════════════════════════

Porta utilizada para comunicação.

Portas comuns:

21    FTP
22    SSH
23    Telnet
25    SMTP
53    DNS
80    HTTP
110   POP3
143   IMAP
443   HTTPS
3306  MySQL
5432  PostgreSQL
8080  HTTP Alternativo

═══════════════════════════════════════════════
[COMO INTERPRETAR OS RESULTADOS]
═══════════════════════════════════════════════

[CONEXÃO ESTABELECIDA]
O serviço está acessível.

────────────────────────────────────────────

[CONNECTION REFUSED]
A máquina respondeu, mas não existe
serviço escutando na porta.

────────────────────────────────────────────

[TIMEOUT]
Nenhuma resposta recebida.

Possíveis causas:

• Firewall
• Porta filtrada
• Host indisponível

────────────────────────────────────────────

[BANNER CAPTURADO]
Informações do serviço foram obtidas.

═══════════════════════════════════════════════
[FLUXO RECOMENDADO NO VAPOREON]
═══════════════════════════════════════════════

1. Nmap
   Descobrir portas abertas.

2. Gobuster / Nikto
   Enumerar aplicações web.

3. SQLMap
   Testar parâmetros suspeitos.

4. Netcat
   Validar conectividade e interagir
   com serviços encontrados.

═══════════════════════════════════════════════
[DICA DE OURO]
═══════════════════════════════════════════════

O Netcat é excelente para entender como
os protocolos funcionam.

Antes de tentar tarefas avançadas,
utilize o modo "Testar Porta" para observar
como serviços reais respondem a conexões.
"""
)

        input_style = INPUT_STYLE

        # Controles
        self.mode = ft.Dropdown(
            label="Como o Netcat deve agir?",
            value="1",
            options=[
                ft.dropdown.Option("1","Ouvir Porta Local (Listener)"),
                ft.dropdown.Option("2","Conectar a um Serviço Remoto (Cliente)"),
                ft.dropdown.Option("3","Testar Porta e Capturar Banner"),
            ],
            **input_style
        )

        self.host = ft.TextField(
            label="Alvo (IP ou Domínio - Deixe vazio se for Ouvir)",
            value="",
            **input_style
        )

        self.port = ft.TextField(
            label="Porta de Comunicação (ex: 4444 ou 80)",
            value="4444",
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.mode,
            self.host,
            self.port,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.mode.value = "Conectar a um Serviço Remoto (Cliente)"
        self.host.value = ""
        self.port.value = "4444"
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    async def run(self, e):

        await self.clear_terminal()

        try:

            self.last_command = await self.controller.execute(
                mode=self.mode.value,
                host=self.host.value,
                port=self.port.value,
                manual_mode=self.free_cmd_switch.value,
                raw_command=self.raw_cmd.value,
                on_output=self.write_terminal,
                tab=self
            )

        except Exception as err:

            await self.write_terminal(
                f"[ERRO] {err}\n"
            )
