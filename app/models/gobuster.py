import shlex
from models.base_tool import BaseTool

class Gobuster(BaseTool):
    @property
    def name(self) -> str: return "Gobuster"
    @property
    def binary(self) -> str: return "gobuster"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, target, mode, wordlist, threads, extensions, status_codes, follow_redirect, timeout, cookies="", raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        mode_map = {
            "Buscar Pastas e Arquivos (dir)": "dir",
            "Descobrir Subdomínios (dns)": "dns",
            "Descobrir Virtual Hosts (vhost)": "vhost"
        }
        actual_mode = mode_map.get(mode, "dir")

        target_flag = "-d" if actual_mode == "dns" else "-u"
        cmd = [self.binary, actual_mode, target_flag, target, "-w", wordlist, "-t", threads, "--timeout", f"{timeout}s"]
        
        if extensions and actual_mode == "dir": cmd += ["-x", extensions]
        if status_codes and actual_mode == "dir": cmd += ["-s", status_codes, "-b", ""]
        if follow_redirect and actual_mode == "dir": cmd += ["-r"]
        if cookies: cmd += ["-c", cookies]
        
        return cmd