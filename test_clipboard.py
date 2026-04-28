import flet as ft
def main(page: ft.Page):
    print("set_clipboard exists:", hasattr(page, 'set_clipboard'))
    print("clipboard exists:", hasattr(page, 'clipboard'))
    print("type of clipboard:", type(page.clipboard))
ft.run(main)
