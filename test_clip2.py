import flet as ft
def main(page: ft.Page):
    cb = ft.Clipboard()
    page.overlay.append(cb)
    page.update()
    cb.set("hello")
    print("Copied")
ft.run(main)
