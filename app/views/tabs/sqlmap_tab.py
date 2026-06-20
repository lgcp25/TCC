import flet as ft
from views.tool_tab import ToolTab
from models.sqlmap import Sqlmap
from config import INPUT_STYLE

class SqlmapTab(ToolTab):
    def __init__(self, app, name, controller):
        self.controller = controller
        super().__init__(
            app, 
            name, 
            "Injeção de Dados / SQLi", 
            "https://github.com/sqlmapproject/sqlmap/wiki/Usage",
            ft.Icons.STORAGE,
            ft.Icons.DATA_OBJECT,
            description="O SQLmap automatiza o processo de detecção e exploração de falhas de Injeção de SQL (SQLi). Ele é capaz de assumir o controle de banco de dados inteiros e extrair tabelas, colunas e senhas.",
            help_text="""GUIA TÉCNICO COMPLETO DO SQLMAP:

╔══════════════════════════════════════════════════════════════╗
║                      SQLMAP - AJUDA                         ║
╚══════════════════════════════════════════════════════════════╝

O SQLMap automatiza a detecção e análise de vulnerabilidades
de SQL Injection (SQLi) em aplicações web.

Ele pode:

• Detectar SQL Injection
• Identificar o banco de dados utilizado
• Enumerar bancos, tabelas e colunas
• Extrair informações permitidas pelo teste
• Automatizar tarefas que manualmente levariam horas

═══════════════════════════════════════════════════════════════
[1] URL ALVO
═══════════════════════════════════════════════════════════════

A URL deve conter parâmetros.

Exemplo válido:

http://dvwa/vulnerabilities/sqli/?id=1

Exemplos de parâmetros:

?id=1
?user=admin
?cat=5

Exemplo inválido:

http://dvwa/

Sem parâmetros o SQLMap não saberá onde testar.

═══════════════════════════════════════════════════════════════
[2] NÍVEL DE INTENSIDADE (--level)
═══════════════════════════════════════════════════════════════

Define quantos pontos da requisição serão testados.

LEVEL 1
    Apenas parâmetros GET e POST.

LEVEL 2
    Inclui Cookies.

LEVEL 3
    Inclui User-Agent e Referer.

LEVEL 4
    Testes adicionais em cabeçalhos HTTP.

LEVEL 5
    Testa praticamente todos os campos possíveis.

Quanto maior o nível:
• Mais testes
• Mais tempo
• Maior chance de encontrar vetores

═══════════════════════════════════════════════════════════════
[3] NÍVEL DE RISCO (--risk)
═══════════════════════════════════════════════════════════════

Controla a agressividade dos testes.

RISK 1
    Mais seguro.
    Recomendado para iniciantes.

RISK 2
    Inclui técnicas adicionais.

RISK 3
    Executa os testes mais agressivos
    disponíveis no SQLMap.

Quanto maior o risco:
• Mais requisições
• Mais impacto no alvo
• Mais cobertura dos testes

═══════════════════════════════════════════════════════════════
[4] TÉCNICA DE INJEÇÃO
═══════════════════════════════════════════════════════════════

TODAS
    O SQLMap escolhe automaticamente.

UNION (U)
    Utiliza consultas UNION.
    Geralmente rápida.

ERROR (E)
    Aproveita mensagens de erro.

BOOLEAN (B)
    Baseada em respostas Verdadeiro/Falso.

TIME (T)
    Baseada em atrasos de resposta.
    Mais lenta.

STACKED (S)
    Utiliza múltiplas consultas.

INLINE (Q)
    Técnica menos comum utilizada em
    cenários específicos.

═══════════════════════════════════════════════════════════════
[5] O QUE EXTRAIR?
═══════════════════════════════════════════════════════════════

LISTAR BANCOS
    Exibe os bancos encontrados.

Exemplo:

• dvwa
• mysql
• information_schema

────────────────────────────────────────

EXTRAIR TABELAS
    Lista tabelas dos bancos encontrados.

Exemplo:

• users
• products
• logs

────────────────────────────────────────

EXTRAIR SENHAS
    Procura credenciais armazenadas
    no banco de dados.

Observação:
Nem toda senha poderá ser recuperada.
Muitas aplicações utilizam hashes.

────────────────────────────────────────

VERIFICAR SHELL
    Procura indícios de execução remota
    disponíveis através do SQL Injection.

═══════════════════════════════════════════════════════════════
[COOKIES AUTOMÁTICOS]
═══════════════════════════════════════════════════════════════

Quando disponível, o Vaporeon utiliza
automaticamente sua sessão autenticada.

Isso permite testar áreas protegidas
por login sem precisar informar os
cookies manualmente.

═══════════════════════════════════════════════════════════════
[INTERPRETANDO RESULTADOS]
═══════════════════════════════════════════════════════════════

[SQL Injection Confirmada]
    O parâmetro é vulnerável.

[Banco Identificado]
    O tipo de banco foi detectado.

[Tabelas Encontradas]
    Estrutura do banco descoberta.

[Dados Recuperados]
    Informações puderam ser enumeradas.

═══════════════════════════════════════════════════════════════
[DICA DE OURO]
═══════════════════════════════════════════════════════════════

Antes de abrir o SQLMap, utilize Nmap,
Gobuster e Nikto.

O SQLMap funciona melhor quando você já
identificou:

• Uma aplicação web
• Um parâmetro interessante
• Um possível ponto de entrada

Quanto melhor a enumeração inicial,
mais eficiente será a análise com SQLMap.
"""
        )

        input_style = INPUT_STYLE

        self.target = ft.TextField(label="URL Alvo (Deve conter parâmetros, ex: ?id=1)", value="http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#", **input_style)
        
        self.level = ft.Dropdown(
            label="Nível de Teste (--level)",
            value="1",
            options=[
                ft.dropdown.Option("1", "1. Padrão - Apenas parâmetros GET/POST"),
                ft.dropdown.Option("2", "2. Moderado - Inclui teste em Cookies"),
                ft.dropdown.Option("3", "3. Avançado - Inclui User-Agent e Referer"),
                ft.dropdown.Option("4", "4. Agressivo - Payloads extras e mais Headers"),
                ft.dropdown.Option("5", "5. Exaustivo - Testa tudo, incluindo Host")
            ],
            **input_style
        )

        self.risk = ft.Dropdown(
            label="Nível de Risco (--risk)",
            value="1",
            options=[
                ft.dropdown.Option("1", "1. Seguro - Apenas consultas de leitura padrão"),
                ft.dropdown.Option("2", "2. Moderado - Adiciona testes de tempo"),
                ft.dropdown.Option("3", "3. Perigoso - Testes agressivos")
            ],
            **input_style
        )

        self.technique = ft.Dropdown(
            label="Técnica de Injeção Preferida (--technique)",
            value="A",
            options=[
                ft.dropdown.Option("A", "Todas (Padrão - Deixa o SQLMap decidir)"),
                ft.dropdown.Option("U", "UNION - Super Rápida"),
                ft.dropdown.Option("E", "Baseada em Erros"),
                ft.dropdown.Option("B", "Cega Booleana"),
                ft.dropdown.Option("T", "Cega por Tempo"),
                ft.dropdown.Option("S", "Consultas Empilhadas"),
                ft.dropdown.Option("Q", "Consultas Em Linha")
            ],
            **input_style
        )
        
        self.db_switch = ft.Switch(label="Listar Nomes dos Bancos de Dados", value=False)
        self.table_switch = ft.Switch(label="Extrair Todas as Tabelas (Demorado)", value=False)
        self.pass_switch = ft.Switch(label="Extrair/Quebrar Senhas", value=False)
        self.shell_switch = ft.Switch(label="Verificar Possibilidade de Execução Remota",value=False)

        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.level,
            self.risk,
            self.technique,
            ft.Row([self.db_switch, self.table_switch, self.pass_switch,self.shell_switch], wrap=True)
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#"
        self.level.value = "1"
        self.risk.value = "1"
        self.technique.value = "A"
        self.db_switch.value = False
        self.table_switch.value = False
        self.pass_switch.value = False
        self.shell_switch = False
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    async def run(self, e):

        await self.clear_terminal()

        try:

            self.last_command = await self.controller.execute(
                target=self.target.value,
                level=self.level.value,
                risk=self.risk.value,
                technique=self.technique.value,
                get_dbs=self.db_switch.value,
                get_tables=self.table_switch.value,
                get_passwords=self.pass_switch.value,
                get_shell=self.shell_switch.value,
                manual_mode=self.free_cmd_switch.value,
                raw_command=self.raw_cmd.value,
                on_output=self.write_terminal,
                tab=self
            )

        except Exception as err:

            await self.write_terminal(
                f"[ERRO] {err}\n"
            )

