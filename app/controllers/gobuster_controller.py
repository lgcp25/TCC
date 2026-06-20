import shlex

from models.gobuster import Gobuster
from services.tool_executor import ToolExecutor
from utils import format_cookies


class GobusterController:

    def __init__(self, app):
        self.app = app
        self.model = Gobuster()
        self.executor = app.executor

    async def execute(
        self,
        target,
        mode,
        wordlist,
        threads,
        extensions,
        status_codes,
        follow_redirect,
        timeout,
        use_cookies,
        manual_mode,
        raw_command,
        on_output,
        tab
    ):

        if tab:
            tab.set_executing(True)

        self.app.set_loading(
            "Scanner em execução...",
            True
        )

        async def on_finish():
            if tab:
                tab.set_executing(False)

            self.app.set_loading(
                "",
                False
            )

        if manual_mode:

            command_str = raw_command

            cmd_list = shlex.split(
                command_str
            )

            await on_output(
                f"[COMANDO] {command_str}\n\n"
            )

            self.executor.execute(
                "pentester",
                cmd_list,
                on_output,
                tab,
                on_finish
            )

            return command_str

        cookie_str = format_cookies(getattr(self.app, "dvwa_cookies", {})) if use_cookies else ""

        cmd_list = self.model.build_command(
            target=target,
            mode=mode,
            wordlist=wordlist,
            threads=threads,
            extensions=extensions,
            status_codes=status_codes,
            follow_redirect=follow_redirect,
            timeout=timeout,
            cookies=cookie_str
        )

        command_str = self.model.pretty_command(
            cmd_list
        )

        await on_output(
            f"[COMANDO] {command_str}\n\n"
        )

        self.executor.execute(
            "pentester",
            cmd_list,
            on_output,
            tab,
            on_finish
        )

        return command_str