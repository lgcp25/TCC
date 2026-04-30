import shlex
from tools.base_tool import BaseTool

class Dirsearch(BaseTool):
    @property
    def name(self) -> str: return "Dirsearch"
    @property
    def binary(self) -> str: return "dirsearch"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, target, wordlist, extensions, http_method, recursion_depth, exclude_status, threads, timeout, lowercase_switch, json_switch, extra_params, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        cmd = [self.binary, "-u", target, "-w", wordlist, "-t", threads, "--timeout", timeout, "-m", http_method]
        
        if extensions: cmd += ["-e", extensions]
        if recursion_depth and int(recursion_depth) > 1: cmd += ["-r", "-R", recursion_depth]
        if exclude_status: cmd += ["-x", exclude_status]
        if lowercase_switch: cmd += ["--lowercase"]
        if json_switch: cmd += ["--json-report", "/results/dirsearch_report.json"]
        if extra_params: cmd += shlex.split(extra_params)
        
        return cmd