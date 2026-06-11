import shlex
from models.base_tool import BaseTool

class Nikto(BaseTool):
    @property
    def name(self) -> str: return "Nikto"
    @property
    def binary(self) -> str: return "/opt/nikto/program/nikto.pl"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, host, port, ssl_switch, tuning, user_agent, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            # Se o usuário digitou "nikto ..." no comando livre, substitui pelo caminho real
            if parts[0] == "nikto": parts[0] = self.binary
            return parts

        tuning_map = {
            "Foco em execução de comandos (Command Execution)": "8",
            "Foco em Injeções (SQLi, XSS, Command Injection)": "149",
            "Foco em Arquivos Vazados (Backups, Configs)": "3bg",
            "Foco em Configurações Erradas e Headers": "02",
            "Varredura Completa (Padrão)": ""
        }
        actual_tuning = tuning_map.get(tuning, "")

        agent_map = {
            "Win11 Chrome":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mac Chrome":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Linux Firefox":"Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
        }
        actual_agent = agent_map.get(user_agent, "")

        cmd = [self.binary, "-h", host]
        
        if port: cmd += ["-p", port]
        if ssl_switch: cmd += ["-ssl"]
        if actual_tuning: cmd += ["-Tuning", actual_tuning]
        if actual_agent: cmd += ["-useragent", actual_agent]
        
        return cmd