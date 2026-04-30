import flet as ft
from ui.tool_tab import ToolTab
from tools.sqlmap import Sqlmap
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
            help_text="""GUIA TÉCNICO SQLMAP:

Ferramenta automática para detecção e exploração de falhas de SQL Injection.

1. EXPLICAÇÃO DOS CAMPOS:
   - URL ALVO: A URL que contém o parâmetro que você suspeita ser vulnerável.
   - NÍVEL (--level): Define a profundidade dos testes. No nível 5, o SQLmap testa até headers HTTP raros e payloads complexos.
   - RISCO (--risk): Define o nível de agressividade. Risco 3 testa técnicas baseadas em 'OR' que podem, em casos raros, apagar ou modificar dados se não houver cuidado.
   - TÉCNICAS (--technique): 
     * B (Boolean): Testa se a página muda baseado em perguntas Verdadeiro/Falso.
     * E (Error): Força o banco a 'cuspir' dados em mensagens de erro.
     * U (Union): A técnica mais rápida, anexa dados extras ao final da query legítima.
     * T (Time): Faz o banco 'dormir' (sleep) para confirmar a falha pelo tempo de resposta.
   - SWITCHES DE EXTRAÇÃO:
     * Listar DBs (--dbs): Mostra os esquemas/bancos disponíveis.
     * Listar Tabelas (--tables): Mostra o conteúdo do banco selecionado.
     * Extrair Senhas (--passwords): Busca a tabela de usuários e tenta realizar o 'crack' dos hashes.

2. EXEMPLOS DE COMANDO GERADO:
   - Detecção Básica: sqlmap -u "http://alvo/p.php?id=1" --batch
   - Extração de Bancos (Agressivo): sqlmap -u "http://alvo/p.php?id=1" --level=5 --risk=3 --dbs
   - Extrair Senhas com Técnica Union: sqlmap -u "http://alvo/p.php?id=1" --technique=U --passwords

4. ENTENDENDO A URL E PARÂMETROS:
   Muitas vezes você verá URLs como: `http://alvo.com/perfil.php?id=10&user=admin`
   - O `?` marca o início dos parâmetros.
   - O `id` e `user` são as 'chaves' (variáveis) que o site processa.
   - O `10` e `admin` são os 'valores'.
   - O `&` separa um parâmetro do outro.
   O SQLmap tenta injetar códigos maliciosos nesses VALORES para ver se o banco de dados do servidor responde de forma inesperada. Se você não colocar o parâmetro na URL (ex: só colocar `http://alvo.com/`), o SQLmap não saberá onde atacar!"""
        )
        self.sqlmap = Sqlmap()

        input_style = INPUT_STYLE

        self.target = ft.TextField(label="URL Alvo", value="http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#", **input_style)
        
        self.level = ft.Dropdown(
            label="Nível de Teste (--level)",
            value="1",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            **input_style
        )
        
        self.risk = ft.Dropdown(
            label="Risco (--risk)",
            value="1",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 4)],
            **input_style
        )

        self.technique = ft.TextField(label="Técnicas (--technique)", value="BEUSTQ", **input_style)
        
        self.db_switch = ft.Switch(label="Listar DBs", value=False)
        self.table_switch = ft.Switch(label="Listar Tabelas", value=False)
        self.pass_switch = ft.Switch(label="Extrair Senhas", value=False)

        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.level,
            self.risk,
            self.technique,
            ft.Row([self.db_switch, self.table_switch, self.pass_switch], wrap=True)
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "http://dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#"
        self.level.value = "1"
        self.risk.value = "1"
        self.technique.value = "BEUSTQ"
        self.db_switch.value = False
        self.table_switch.value = False
        self.pass_switch.value = False
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
                cmd_list = [self.sqlmap.binary] + shlex.split(self.raw_cmd.value)
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
                    cookies_str=cookies_str
                )
            
            self.last_command = self.sqlmap.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.sqlmap.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"ERRO: {err}")
