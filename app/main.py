import flet as ft
import logging
from controllers.main_controller import PentesterApp

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

async def main(page: ft.Page):
    page.window.maximized = True
    app = PentesterApp(page)
    await app.initialize()

if __name__ == "__main__":
    ft.run(main)