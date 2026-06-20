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

        if mode == "1":
            cmd += ["-sT", "--top-ports", "1000", "-sV"]

        elif mode == "2":
            cmd += ["-p-", "-sT", "-sV", "-O", "-T4"]

        elif mode == "3":
            cmd += ["-A", "-T4"]

        elif mode == "4":
            cmd += ["-p-", "--open", "-sV"]

        elif mode == "5":
            if not valid_port(port):
                raise ValueError("Porta inválida.")
            cmd += ["-p", port, "-sV"]

        elif mode == "6":
            cmd += ["-sU", "--top-ports", "1000"]

        elif mode == "7":
            cmd += ["-sn"]

        elif mode == "8":
            cmd += ["-O"]

        elif mode == "9":
            cmd += ["-sV"]

        elif mode == "10":
            cmd += ["-sS", "-sV"]

        elif mode == "11":
            cmd += ["--script", "safe"]

        elif mode == "12":
            cmd += ["-p", "80,443", "--script", "http-title,http-headers"]

        elif mode == "13":
            cmd += ["-p", "443", "--script", "ssl-cert"]

        elif mode == "14":
            cmd += ["-p", "445", "--script", "smb-enum-shares"]

        elif mode == "15":
            cmd += ["-p", "445", "--script", "smb-enum-users"]

        elif mode == "16":
            cmd += ["-F", "-sV"]

        elif mode == "17":
            cmd += ["-p", "80,443,8080,8443", "-sV", "--script", "http-title"]

        elif mode == "18":
            cmd += ["-R", "-sV"]

        elif mode == "19":
            cmd += ["-sn", "-PE"]

        elif mode == "20":
            cmd += ["-sS", "-sV", "-O", "--top-ports", "1000"]

        if os_detect and "-O" not in cmd and "-A" not in cmd:
            cmd.append("-O")

        if script_scan != "":
            cmd += ["--script", script_scan]
            

        if verbose:
            cmd.append("-v")

        cmd.append(target)
        
        return cmd
