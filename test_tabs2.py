import flet as ft
def main(page):
    try:
        tb = ft.TabBar(tabs=[ft.Tab(label="1"), ft.Tab(label="2")])
        tv = ft.TabBarView(controls=[ft.Text("A"), ft.Text("B")])
        page.add(ft.Tabs(length=2, content=ft.Column([tb, tv])))
        print("SUCCESS")
    except Exception as e:
        print("ERROR:", e)
ft.app(target=main)
