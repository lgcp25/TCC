from shared_imports import sanitize, valid_url
import shlex

class Sqlmap:
    def build_sqlmap_command(self, target, mode, param=None, data=None):
        target = sanitize(target)
        if not valid_url(target):
            raise ValueError("URL inválida")

        param = sanitize(param)
        data = sanitize(data)

        # Comando base
        cmd = ["sqlmap", "-u", target, "--batch"]

        if mode == "Teste básico de SQLi (--batch)":
            if data:
                cmd += ["--data", data]

        elif mode == "Enumerar bancos (--dbs)":
            cmd += ["--dbs"]

        elif mode == "Testar parâmetro específico (-p)":
            if not param:
                raise ValueError("Parâmetro obrigatório para este modo")
            cmd += ["-p", param]

        elif mode == "SQLi agressivo (level 5 / risk 3)":
            cmd += ["--level", "5", "--risk", "3"]
            if data:
                cmd += ["--data", data]

        return cmd

    def pretty_command(self, cmd):
        return " ".join(shlex.quote(c) for c in cmd)
