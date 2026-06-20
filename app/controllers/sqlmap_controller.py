import shlex

from models.sqlmap import Sqlmap
from services.tool_executor import ToolExecutor
from utils import format_cookies


class SqlmapController:

    def __init__(self, app):

        self.app = app
        self.model = Sqlmap()
        self.executor = app.executor

    async def execute(
        self,
        target,
        level,
        risk,
        technique,
        get_dbs,
        get_tables,
        get_passwords,
        get_shell,
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

            cmd_list = self.model.build_command(
                target=None,
                raw_cmd=raw_command
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

        cookies_str = format_cookies(getattr(self.app, "dvwa_cookies", {}))

        cmd_list = self.model.build_command(
            target=target,
            level=level,
            risk=risk,
            technique=technique,
            get_dbs=get_dbs,
            get_tables=get_tables,
            get_passwords=get_passwords,
            get_shell=get_shell,
            cookies_str=cookies_str
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