import flet as ft
def main(page):
    page.add(ft.Tabs(
        length=2,
        content=ft.Column([
            ft.TabBar(tabs=[ft.Tab(text="1"), ft.Tab(text="2")]),
            ft.TabBarView(content=[ft.Text("A"), ft.Text("B")])
        ])
    ))
ft.app(target=main)
