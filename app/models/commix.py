import shlex
from models.base_tool import BaseTool

class Commix(BaseTool):
    @property
    def name(self) -> str: return "Commix"
    @property
    def binary(self) -> str: return "commix"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, url, data, cookie, header, technique, os_cmd_switch, os_shell_switch, json_switch, extra_params, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        cmd = [self.binary, "--url", url, "--batch"]
        
        if data: cmd += ["--data", data]
        if cookie: cmd += ["--cookie", cookie]
        if header: cmd += ["--headers", header]
        if technique: cmd += ["--technique", technique]
        
        if os_cmd_switch: cmd += ["--os-cmd", "whoami"] # Default test payload
        if os_shell_switch: cmd += ["--os-shell"] # Aviso: shell interativo pode não funcionar bem via script
        
        if extra_params: cmd += shlex.split(extra_params)
        
        return cmd