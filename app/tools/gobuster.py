import shlex
from tools.base_tool import BaseTool

class Gobuster(BaseTool):
    @property
    def name(self) -> str: return "Gobuster"
    @property
    def binary(self) -> str: return "gobuster"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, target, mode, wordlist, threads, extensions, status_codes, follow_redirect, timeout, extra_params, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        cmd = [self.binary, mode, "-u", target, "-w", wordlist, "-t", threads, "--timeout", f"{timeout}s"]
        
        if extensions and mode == "dir": cmd += ["-x", extensions]
        if status_codes and mode == "dir": cmd += ["-s", status_codes]
        if follow_redirect and mode == "dir": cmd += ["-r"]
        if extra_params: cmd += shlex.split(extra_params)
        
        return cmd