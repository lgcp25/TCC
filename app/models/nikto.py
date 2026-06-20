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
            if parts[0] == "nikto": parts[0] = self.binary
            return parts

        tuning_map = {
            "1": "",
            "2": "8",
            "3": "149",
            "4": "3bg",
            "5": "02"
        }
        actual_tuning = tuning_map.get(tuning, "")

        agent_map = {
            "1":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "2":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "3":"Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
        }
        actual_agent = agent_map.get(user_agent, "")

        cmd = [self.binary, "-h", host]
        
        if port: cmd += ["-p", port]
        if ssl_switch: cmd += ["-ssl"]
        if actual_tuning: cmd += ["-Tuning", actual_tuning]
        if actual_agent: cmd += ["-useragent", actual_agent]
        
        return cmd