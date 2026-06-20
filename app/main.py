import flet as ft
import logging
from controllers.main_controller import MainController
from config import THEME_BG

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

async def main(page: ft.Page):
    page.title = "Vaporeon - Pentester Suite"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = THEME_BG
    page.padding = 0
    page.window.maximized = True
    page.fonts = {
        "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
    }

    app = MainController(page)
    await app.initialize()

if __name__ == "__main__":
    ft.run(main)