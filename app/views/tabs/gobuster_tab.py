import flet as ft
from views.tool_tab import ToolTab
from config import INPUT_STYLE


class GobusterTab(ToolTab):
    def __init__(self, app, name, controller):
        self.controller = controller
        super().__init__(
            app,
            name,
            "Enumeração / Brute-Force",
            "https://github.com/OJ/gobuster",
            ft.Icons.FOLDER_OPEN,
            ft.Icons.MANAGE_SEARCH,
            description="O Gobuster é uma ferramenta usada para descobrir URLs, diretórios e arquivos escondidos em servidores web via força bruta rápida utilizando wordlists pesadas.",
            help_text="""GUIA TÉCNICO COMPLETO DO GOBUSTER:

╔══════════════════════════════════════════════════════════════╗
║                      GOBUSTER - AJUDA                       ║
╚══════════════════════════════════════════════════════════════╝

O Gobuster é uma ferramenta de enumeração utilizada para descobrir
diretórios, arquivos, subdomínios e virtual hosts ocultos.

═══════════════════════════════════════════════════════════════
[1] ALVO (URL OU DOMÍNIO)
═══════════════════════════════════════════════════════════════

O endereço que será analisado.

Exemplos:
• http://dvwa
• http://192.168.1.10
• https://empresa.com

IMPORTANTE:
Sempre informe http:// ou https://.

═══════════════════════════════════════════════════════════════
[2] MODO DE OPERAÇÃO
═══════════════════════════════════════════════════════════════

[DIR] Buscar Pastas e Arquivos
      Descobre diretórios e arquivos ocultos.

      Exemplos:
      • /admin
      • /backup.zip
      • /config.php
      • /login

      É o modo mais utilizado durante um pentest web.

[DNS] Descobrir Subdomínios
      Procura servidores relacionados ao domínio.

      Exemplos:
      • api.empresa.com
      • dev.empresa.com
      • mail.empresa.com

[VHOST] Descobrir Virtual Hosts
        Procura sites hospedados no mesmo IP.

        Útil quando múltiplos domínios utilizam
        o mesmo servidor.

═══════════════════════════════════════════════════════════════
[3] WORDLIST
═══════════════════════════════════════════════════════════════

Arquivo contendo as palavras que serão testadas.

common.txt
    Lista básica para reconhecimento rápido.

subdomains.txt
    Lista focada em descoberta de subdomínios
    e virtual hosts.

Quanto melhor a wordlist, melhores os resultados.

═══════════════════════════════════════════════════════════════
[4] THREADS
═══════════════════════════════════════════════════════════════

Quantidade de requisições simultâneas.

Valores recomendados:

10   = Muito estável
25   = Conservador
50   = Equilibrado
100  = Agressivo

Valores altos podem:
• Sobrecarregar o alvo
• Acionar WAFs
• Gerar bloqueios

═══════════════════════════════════════════════════════════════
[5] EXTENSÕES
═══════════════════════════════════════════════════════════════

Utilizado apenas no modo DIR.

Permite procurar arquivos específicos.

Exemplo:

php,bak,zip

A palavra "admin" gera:

• admin.php
• admin.bak
• admin.zip

Extensões interessantes:

• php
• asp
• aspx
• jsp
• txt
• bak
• old
• conf
• ini
• sql
• zip
• json
• xml
• log

═══════════════════════════════════════════════════════════════
[6] STATUS HTTP DE INTERESSE
═══════════════════════════════════════════════════════════════

Códigos que serão exibidos nos resultados.

200 = Página encontrada
301 = Redirecionamento permanente
302 = Redirecionamento temporário
401 = Requer autenticação
403 = Existe, mas acesso negado

DICA:
Resultados 403 costumam ser extremamente
interessantes durante a enumeração.

═══════════════════════════════════════════════════════════════
[7] SEGUIR REDIRECIONAMENTOS
═══════════════════════════════════════════════════════════════

Quando habilitado, o Gobuster segue páginas
que redirecionam automaticamente para outro local.

Útil para aplicações modernas.

═══════════════════════════════════════════════════════════════
[8] COOKIES DE SESSÃO
═══════════════════════════════════════════════════════════════

Envia automaticamente sua sessão autenticada.

Útil quando:

• Você já está logado
• O conteúdo só aparece após login
• O alvo redireciona visitantes para /login

═══════════════════════════════════════════════════════════════
[9] TIMEOUT
═══════════════════════════════════════════════════════════════

Tempo máximo de espera por resposta.

Valores recomendados:

5s  = Rede rápida
10s = Padrão
20s = Servidores lentos

═══════════════════════════════════════════════════════════════
[DICA DE OURO]
═══════════════════════════════════════════════════════════════

Muitos pentests começam encontrando recursos esquecidos:

• /admin
• /backup
• /old
• /test
• /config.php.bak
• /database.sql
• /dev

Nem sempre uma vulnerabilidade aparece logo no início.
A enumeração detalhada costuma revelar caminhos
que os desenvolvedores esqueceram de proteger.
"""
        )

        input_style = INPUT_STYLE

        # Controles
        self.target = ft.TextField(
            label="Alvo (URL ou IP)",
            value="http://dvwa",
            **input_style
        )

        self.mode = ft.Dropdown(
            label="O que você quer procurar?",
            value="1",
            on_select=self.disable_status,
            options=[
                ft.dropdown.Option("1", "1. Buscar Pastas e Arquivos (dir)"),
                ft.dropdown.Option("2", "2. Descobrir Subdomínios (dns)"),
                ft.dropdown.Option("3", "3. Descobrir Virtual Hosts (vhost)")
            ],
            **input_style
        )

        self.wordlist = ft.Dropdown(
            label="Dicionário / Wordlist (Arquivo com as tentativas)",
            value="/wordlists/common.txt",
            options=[
                ft.dropdown.Option(key="/wordlists/common.txt", text="Diretórios e Arquivos Comuns (common.txt)"),
                ft.dropdown.Option(key="/wordlists/subdomains.txt", text="Lista de Subdomínios, utilizado para vhost (subdomains.txt)")
            ],
            **input_style
        )

        self.threads = ft.TextField(
            label="Tarefas Simultâneas (Threads - +Rápido, porém +Barulhento)",
            value="50",
            **input_style
        )
        

        self.extensions = ft.TextField(
            label="Buscar por extensões (ex: php,txt,bak) - Só p/ Arquivos",
            value="php,txt,bak,json,zip,sql,xml,log, jsp,aspx,html,htm,conf,ini,old,config",
            **input_style
        )
        
        self.status_codes = ft.TextField(
                label="Status HTTP Considerados Sucesso (ex: 200,301,403)",
                value="200,300,301,302,307,401,403",
                **input_style
            )
        

        self.follow_redirect = ft.Switch(
            label="Seguir Redirecionamentos de Página",
            value=True,
            active_color=ft.Colors.GREEN_400
        )

        self.use_cookies = ft.Switch(
            label="Usar Cookies da Sessão DVWA",
            value=True,
            active_color=ft.Colors.BLUE_400
        )

        self.timeout = ft.TextField(
            label="Tempo máximo de espera pelo servidor (Segundos)",
            value="10",
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.mode,
            self.wordlist,
            self.threads,
            self.extensions,
            self.status_codes,
            self.follow_redirect,
            self.use_cookies,
            self.timeout,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "http://dvwa:80"
        self.mode.value = "1"
        self.wordlist.value = "/wordlists/common.txt"
        self.threads.value = "10"
        self.extensions.value = ""
        self.status_codes.value = "200,204,301,302,307,401,403"
        self.follow_redirect.value = False
        self.use_cookies.value = True
        self.timeout.value = "10"
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    async def disable_status(self,e):
        if self.mode.value == "3":
            self.status_codes.disabled = True
            self.status_codes.value = "Não aplicável no modo VHost"
        else:
            self.status_codes.disabled = False
            self.status_codes.value = "200,300,301,302,307,401,403"
        self.left_col.update()
              


    async def run(self, e):

        await self.clear_terminal()

        try:

            self.last_command = await self.controller.execute(
                target=self.target.value,
                mode=self.mode.value,
                wordlist=self.wordlist.value,
                threads=self.threads.value,
                extensions=self.extensions.value,
                status_codes=self.status_codes.value,
                follow_redirect=self.follow_redirect.value,
                timeout=self.timeout.value,
                use_cookies=self.use_cookies.value,
                manual_mode=self.free_cmd_switch.value,
                raw_command=self.raw_cmd.value,
                on_output=self.write_terminal,
                tab=self
            )

        except Exception as err:

            await self.write_terminal(
                f"[ERRO] {err}\n"
            )