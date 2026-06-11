from models.base_tool import BaseTool
from utils import sanitize, valid_url, valid_port


class Nmap(BaseTool):

    @property
    def name(self) -> str:
        return "Nmap"

    @property
    def binary(self) -> str:
        return "nmap"

    @property
    def docker_service(self) -> str:
        return "pentester"

    def build_command(self, target, mode, port=None, os_detect=False, script_scan="", verbose=False, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        target = sanitize(target)
        if not valid_url(target):
            raise ValueError("Alvo inválido.")
        
        
        cmd = [self.binary]

        if mode == "1. Scan Rápido (Top 1000 portas)":
            cmd += ["-sT", "--top-ports", "1000", "-sV"]

        elif mode == "2. Varredura Profunda (Lento, mas com bom retorno)":
            cmd += ["-p-", "-sT", "-sV", "-O", "-T4"]

        elif mode == "3. Scan Agressivo (Barulhento, traz muitos dados)":
            cmd += ["-A", "-T4"]

        elif mode == "4. Mapear Todas as Portas (1 a 65535)":
            cmd += ["-p-", "--open", "-sV"]

        elif mode == "5. Investigar Porta Específica":
            if not valid_port(port):
                raise ValueError("Porta inválida.")
            cmd += ["-p", port, "-sV"]

        elif mode == "6. Scan de Portas UDP (Mais lento)":
            cmd += ["-sU", "--top-ports", "1000"]

        elif mode == "7. Descobrir Hosts Ativos na Rede":
            cmd += ["-sn"]

        elif mode == "8. Detectar Sistema Operacional":
            cmd += ["-O"]

        elif mode == "9. Identificar Versões dos Serviços":
            cmd += ["-sV"]

        elif mode == "10. Scan SYN (Rápido e Eficiente)":
            cmd += ["-sS", "-sV"]

        elif mode == "11. Executar Scripts NSE Seguros":
            cmd += ["--script", "safe"]

        elif mode == "12. Analisar Servidor Web (HTTP/HTTPS)":
            cmd += ["-p", "80,443", "--script", "http-title,http-headers"]

        elif mode == "13. Verificar Certificado SSL/TLS":
            cmd += ["-p", "443", "--script", "ssl-cert"]

        elif mode == "14. Descobrir Compartilhamentos SMB":
            cmd += ["-p", "445", "--script", "smb-enum-shares"]

        elif mode == "15. Enumerar Usuários SMB":
            cmd += ["-p", "445", "--script", "smb-enum-users"]

        elif mode == "16. Detectar Serviços Comuns (Fast Scan)":
            cmd += ["-F", "-sV"]

        elif mode == "17. Scan Web Completo (80,443,8080,8443)":
            cmd += ["-p", "80,443,8080,8443", "-sV", "--script", "http-title"]

        elif mode == "18. Scan com Resolução DNS":
            cmd += ["-R", "-sV"]

        elif mode == "19. Descobrir Hosts e Serviços Básicos":
            cmd += ["-sn", "-PE"]

        elif mode == "20. Scan Balanceado (Recomendado para Iniciantes)":
            cmd += ["-sS", "-sV", "-O", "--top-ports", "1000"]

        if os_detect and "-O" not in cmd and "-A" not in cmd:
            cmd.append("-O")

        if script_scan != "":
            script_flag = f"--script={script_scan}"
            cmd.append(script_flag)
            

        if verbose:
            cmd.append("-v")

        cmd.append(target)
        
        return cmd
