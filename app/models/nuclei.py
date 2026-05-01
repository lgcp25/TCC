from models.base_tool import BaseTool
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
                      rate_limit="150", update_templates=False, headers=None, tags=None, raw_cmd=None):
        
        # Apenas as flags essenciais para o app
        system_flags = ["-ni", "-no-color"]

        if raw_cmd:
            parts = shlex.split(raw_cmd)
            if not parts: return [self.binary] + system_flags
            if parts[0] == self.binary: parts = parts[1:]
            return [self.binary] + system_flags + parts

        cmd = [self.binary] + system_flags + ["-u", target]

        # Tags
        if tags:
            cmd += ["-tags", tags]

        # Grupo de templates - Usando caminhos relativos (padrão do Nuclei)
        mapping = {
            "CVEs": "cves/",
            "Vulnerabilidades Web": "vulnerabilities/",
            "Painéis Expostos": "exposures/",
            "Configurações Padrão": "default-logins/",
            "Tecnologias": "technologies/",
            "Fuzzing": "fuzzing/",
            "Helpers": "helpers/"
        }
        
        if template_group in mapping:
            cmd += ["-t", mapping[template_group]]
            
        # Severidade
        if severity and severity != "Todas":
            cmd += ["-severity", severity.lower()]

        # Rate Limit
        if rate_limit:
            cmd += ["-rl", str(rate_limit)]

        # Headers (Cookies do DVWA)
        if headers:
            for key, value in headers.items():
                cmd += ["-H", f"{key}: {value}"]

        return cmd
