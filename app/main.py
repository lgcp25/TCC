import flet as ft
from controller import PentesterApp

async def main(page: ft.Page):
    app = PentesterApp(page)
    await app.initialize()

if __name__ == "__main__":
    ft.run(main)