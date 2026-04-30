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

    def build_command(self, target, mode, port=None, timing="", os_detect=False, script_scan="", verbose=False, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        target = sanitize(target)
        if not valid_url(target):
            raise ValueError("Alvo inválido.")

        cmd = [self.binary]

        if mode == "Ver portas abertas (varre todas as portas, pode demorar)":
            cmd += ["-p-", "--open", "-sV"]
        elif mode == "Scan portas comuns (top 1000)":
            cmd += ["-sT", "--top-ports", "1000", "-sV"]
        elif mode == "Scan porta específica (usar campo Porta)":
            if not valid_port(port):
                raise ValueError("Porta inválida.")
            cmd += ["-p", port, "-sV"]
        elif mode == "Varredura completa TCP com detecção de SO e versões (-p- -sS -sV -O)":
            cmd += ["-p-", "-sT", "-sV", "-O", "-T4"]
        elif mode == "Scan agressivo (scripts default + OS + version) (-A)":
            cmd += ["-A", "-T4"]
        elif mode == "UDP scan (top 1000) (-sU)":
            cmd += ["-sU", "--top-ports", "1000"]
        elif mode == "Usar scripts de vulnerabilidade (--script vuln)":
            cmd += ["-sV", "--script", "vuln"]

        # Adiciona Timing customizado se selecionado e não embutido na receita
        if timing:
            # Verifica se já existe algum -T no comando
            if not any(arg.startswith("-T") for arg in cmd):
                cmd.append(timing)

        # Adiciona Detecção de SO extra
        if os_detect and "-O" not in cmd and "-A" not in cmd:
            cmd.append("-O")

        # Adiciona Script customizado (evitando duplicatas)
        if script_scan and script_scan != "default":
            script_flag = f"--script={script_scan}"
            # Verifica se o script já não foi adicionado via perfil (ex: --script vuln)
            if not any(script_scan in arg for arg in cmd):
                cmd.append(script_flag)

        if verbose:
            cmd.append("-v")

        # Final: alvo
        cmd.append(target)
        return cmd
