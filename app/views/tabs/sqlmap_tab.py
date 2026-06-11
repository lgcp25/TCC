import flet as ft
from views.tool_tab import ToolTab
from models.sqlmap import Sqlmap
from config import INPUT_STYLE

class SqlmapTab(ToolTab):
    def __init__(self, app, name):
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
        self.sqlmap = Sqlmap()

        input_style = INPUT_STYLE

        self.target = ft.TextField(label="URL Alvo (Deve conter parâmetros, ex: ?id=1)", value="http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#", **input_style)
        
        self.level = ft.Dropdown(
        label="Nível de Teste (--level)",
        value="1 (Padrão) - Apenas parâmetros GET/POST",
        options=[
            ft.dropdown.Option("1 (Padrão) - Apenas parâmetros GET/POST"),
            ft.dropdown.Option("2 (Moderado) - Inclui teste em Cookies"),
            ft.dropdown.Option("3 (Avançado) - Inclui User-Agent e Referer"),
            ft.dropdown.Option("4 (Agressivo) - Payloads extras e mais Headers"),
            ft.dropdown.Option("5 (Exaustivo) - Testa tudo, incluindo Host - Lento")
        ],
        **input_style
)

        
        self.risk = ft.Dropdown(
            label="Nível de Risco (--risk)",
            value="1 (Seguro) - Apenas consultas de leitura padrão",
            options=[
                ft.dropdown.Option("1 (Seguro) - Apenas consultas de leitura padrão"),
                ft.dropdown.Option("2 (Moderado) - Adiciona testes de tempo - Pode causar lentidão"),
                ft.dropdown.Option("3 (Perigoso) - Testes agressivos - Risco de alterar dados")
            ],
            **input_style
        )

        self.technique = ft.Dropdown(
            label="Técnica de Injeção Preferida (--technique)",
            value="Tentar Todas (Padrão - Deixa o sqlmap decidir)",
            options=[
                ft.dropdown.Option("Tentar Todas (Padrão - Deixa o sqlmap decidir)"),
                ft.dropdown.Option("U - UNION: Super Rápida (Dados aparecem direto na tela)"),
                ft.dropdown.Option("E - Baseada em Erros: Rápida (Aproveita erros exibidos no site)"),
                ft.dropdown.Option("B - Cega Booleana: Lenta (Para quando o site não mostra erros)"),
                ft.dropdown.Option("T - Cega por Tempo: Muito Lenta (Usa pausas para adivinhar os dados)"),
                ft.dropdown.Option("S - Consultas Empilhadas: Avançada (Para rodar comandos no servidor)"),
                ft.dropdown.Option("Q - Consultas Em Linha: Rara (Para contornar filtros muito restritos)")
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
        self.level.value = "1 (Padrão) - Injeta apenas na URL (Rápido)"
        self.risk.value = "1 (Seguro) - Sem chance de alterar dados"
        self.technique.value = "Todas as Técnicas (Recomendado)"
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
            if self.free_cmd_switch.value:
                # Usa o model para processar o comando manual e evitar duplicidade do binário
                cmd_list = self.sqlmap.build_command(target=None, raw_cmd=self.raw_cmd.value)
            else:
                # Prepara o cookie do DVWA
                cookies_str = None
                if self.app.dvwa_cookies:
                    cookies_str = "; ".join([f"{k}={v}" for k, v in self.app.dvwa_cookies.items()])

                cmd_list = self.sqlmap.build_command(
                    target=self.target.value,
                    level=self.level.value,
                    risk=self.risk.value,
                    technique=self.technique.value,
                    get_dbs=self.db_switch.value,
                    get_tables=self.table_switch.value,
                    get_passwords=self.pass_switch.value,
                    get_shell=self.shell_switch.value,
                    cookies_str=cookies_str
                )
            
            self.last_command = self.sqlmap.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            
            await self.app.run_docker(self.sqlmap.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO NO APP] {err}\n")

