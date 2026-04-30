import shlex
from tools.base_tool import BaseTool

class Nikto(BaseTool):
    @property
    def name(self) -> str: return "Nikto"
    @property
    def binary(self) -> str: return "nikto"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, host, port, ssl_switch, tuning, plugins, user_agent, json_switch, extra_params, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        cmd = [self.binary, "-h", host]
        
        if port: cmd += ["-p", port]
        if ssl_switch: cmd += ["-ssl"]
        if tuning: cmd += ["-Tuning", tuning]
        if plugins: cmd += ["-Plugins", plugins]
        if user_agent: cmd += ["-useragent", user_agent]
        if json_switch: cmd += ["-Format", "json", "-o", "/results/nikto_report.json"]
        if extra_params: cmd += shlex.split(extra_params)
        
        return cmd