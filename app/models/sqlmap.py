from models.base_tool import BaseTool
from utils import sanitize, valid_url


class Sqlmap(BaseTool):

    @property
    def name(self) -> str:
        return "SQLmap"

    @property
    def binary(self) -> str:
        return "sqlmap"

    @property
    def docker_service(self) -> str:
        return "pentester"

    def build_command(self, target, level, risk, technique, 
                      get_dbs=False, get_tables=False, get_passwords=False,get_shell=False, cookies_str=None, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if not parts: return [self.binary]
            if parts[0] == "sqlmap": parts[0] = self.binary
            return parts

        # Comando base
        cmd = [self.binary, "-u", target, "--batch", "--random-agent"]
        
        if cookies_str:
            cmd += ["--cookie", cookies_str]
            
        # Parse Level and Risk (Extract the first character which is the number)
        parsed_level = level[0] if level else "1"
        parsed_risk = risk[0] if risk else "1"
        
        # Parâmetros de profundidade
        cmd += ["--level", parsed_level, "--risk", parsed_risk]
        
        # Parse Technique
        technique_map = {
            "Tentar Todas (Padrão - Deixa o sqlmap decidir)": "BEUSTQ",
            "U - UNION: Super Rápida (Dados aparecem direto na tela)": "U",
            "E - Baseada em Erros: Rápida (Aproveita erros exibidos no site)": "E",
            "B - Cega Booleana: Lenta (Para quando o site não mostra erros)": "B",
            "T - Cega por Tempo: Muito Lenta (Usa pausas para adivinhar os dados)": "T",
            "S - Consultas Empilhadas: Avançada (Para rodar comandos no servidor)": "S",
            "Q - Consultas Em Linha: Rara (Para contornar filtros muito restritos)": "Q"
        }
        parsed_technique = technique_map.get(technique, "BEUSTQ")
        
        if parsed_technique:
            cmd += ["--technique", parsed_technique]
            
        # Ações de extração
        if get_dbs:
            cmd += ["--dbs"]
        if get_tables:
            cmd += ["--tables"]
        if get_passwords:
            cmd += ["--passwords"]
        if get_shell:
            cmd += ["--os-shell"]

        return cmd
