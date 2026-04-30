from tools.base_tool import BaseTool
from utils import sanitize, valid_url
import shlex

class Nuclei(BaseTool):

    @property
    def name(self) -> str:
        return "Nuclei"

    @property
    def binary(self) -> str:
        return "nuclei"

    @property
    def docker_service(self) -> str:
        return "pentester"

    def build_command(self, target, template_group="Todos (Padrão)", severity="Todas", 
                      rate_limit="150", update_templates=False, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if not parts: return [self.binary]
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        cmd = [self.binary, "-u", target]

        # Grupo de templates
        if template_group == "CVEs":
            cmd += ["-t", "cves/"]
        elif template_group == "Web Vulnerabilities":
            cmd += ["-t", "vulnerabilities/"]
        elif template_group == "Default Login":
            cmd += ["-t", "default-logins/"]
        elif template_group == "Exposures":
            cmd += ["-t", "exposures/"]
            
        # Severidade
        if severity and severity != "Todas":
            cmd += ["-severity", severity.lower()]

        # Rate Limit
        if rate_limit:
            cmd += ["-rl", str(rate_limit)]

        # Update
        if update_templates:
            cmd += ["-ut"]

        return cmd
