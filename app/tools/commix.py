from shared_imports import *

class Commix(tb.Frame):
    def __init__(self, master):
        super.__init__(master)
# ============================================================
# =========================  ABA COMMIX  =======================
# ============================================================
def build_commix_tab(self):
    tab = self.tabs["Commix"]

    # ============================================================
    # FORMULÁRIO PRINCIPAL
    # ============================================================
    form = ttk.Labelframe(tab, text="Configuração do Commix")
    form.pack(fill="x", padx=10, pady=10)

    ttk.Label(form, text="URL alvo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.cx_url = ttk.Entry(form, width=60)
    self.cx_url.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(form, text="POST data (opcional):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    self.cx_data = ttk.Entry(form, width=60)
    self.cx_data.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    # Cookie
    ttk.Label(form, text="Cookie (opcional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    self.cx_cookie = ttk.Entry(form, width=60)
    self.cx_cookie.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    # Header
    ttk.Label(form, text="Header customizado (User-Agent, etc):").grid(
        row=3, column=0, sticky="w", padx=5, pady=5
    )
    self.cx_header = ttk.Entry(form, width=60)
    self.cx_header.grid(row=3, column=1, sticky="w", padx=5, pady=5)

    # ============================================================
    # OPÇÕES AVANÇADAS
    # ============================================================
    adv = ttk.Labelframe(tab, text="Opções avançadas")
    adv.pack(fill="x", padx=10, pady=10)

    # Técnicas
    ttk.Label(adv, text="Técnica (-technique):").grid(row=0, column=0, sticky="w", padx=5)
    self.cx_technique = ttk.Entry(adv, width=20)
    self.cx_technique.insert(0, "se")
    self.cx_technique.grid(row=0, column=1, sticky="w", padx=5)

    # OS command
    self.cx_os_cmd = tk.BooleanVar()
    ttk.Checkbutton(adv, text="OS Command Injection (-os-cmd)",
                    variable=self.cx_os_cmd).grid(
        row=1, column=1, sticky="w", padx=5
    )

    # OS shell
    self.cx_os_shell = tk.BooleanVar()
    ttk.Checkbutton(adv, text="OS Interactive Shell (-os-shell)",
                    variable=self.cx_os_shell).grid(
        row=2, column=1, sticky="w", padx=5
    )

    # Output JSON
    self.cx_json = tk.BooleanVar()
    ttk.Checkbutton(adv, text="Salvar saída JSON (--output-json)",
                    variable=self.cx_json).grid(
        row=3, column=1, sticky="w", padx=5, pady=5
    )

    # Extras
    ttk.Label(adv, text="Extras:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    self.cx_extra = ttk.Entry(adv, width=60)
    self.cx_extra.grid(row=4, column=1, sticky="w", padx=5, pady=5)

    # ============================================================
    # OUTPUT
    # ============================================================
    self.cx_output = tk.Text(tab, wrap="word", height=22)
    self.cx_output.pack(fill="both", expand=True, padx=10, pady=10)

    # ============================================================
    # BOTÕES
    # ============================================================
    btns = ttk.Frame(tab)
    btns.pack(fill="x", pady=10)

    ttk.Button(btns, text="Gerar Comando", bootstyle="secondary",
                command=self.cx_generate).pack(side="left", padx=5)

    ttk.Button(btns, text="Executar", bootstyle="success",
                command=self.cx_execute).pack(side="left", padx=5)

    ttk.Button(btns, text="Cancelar", bootstyle="danger",
                command=self.cancel_process).pack(side="left", padx=5)

    ttk.Button(btns, text="Limpar", bootstyle="info",
                command=lambda: self.cx_output.delete("1.0", "end")).pack(side="left", padx=5)


# ============================================================
# FUNÇÕES — COMMIX
# ============================================================
def cx_generate(self):
    self.cx_output.delete("1.0", "end")
    try:
        cmd = self.build_commix_command()
        pretty = " ".join(shlex.quote(c) for c in cmd)
        self.cx_output.insert("end", pretty + "\n")
    except Exception as e:
        self.cx_output.insert("end", f"[ERRO] {e}\n")


def build_commix_command(self):
    url = sanitize(self.cx_url.get())
    data = sanitize(self.cx_data.get())
    cookie = sanitize(self.cx_cookie.get())
    header = sanitize(self.cx_header.get())
    technique = sanitize(self.cx_technique.get())
    extra = sanitize(self.cx_extra.get())

    if not valid_url(url):
        raise ValueError("URL inválida.")

    cmd = ["commix", "--batch", "--url", url]

    if data:
        cmd += ["--data", data]

    if cookie:
        cmd += ["--cookie", cookie]

    if header:
        cmd += ["--headers", header]

    if technique:
        cmd += ["--technique", technique]

    if self.cx_os_cmd.get():
        cmd.append("--os-cmd")

    if self.cx_os_shell.get():
        cmd.append("--os-shell")

    if self.cx_json.get():
        cmd += ["--output-json", "/work/output/commix.json"]

    if extra:
        cmd += shlex.split(extra)

    return cmd


def cx_execute(self):
    self.cx_output.delete("1.0", "end")

    try:
        cmd = self.build_commix_command()
    except Exception as e:
        self.cx_output.insert("end", f"[ERRO] {e}\n")
        return

    self.run_docker("pentester", cmd, self.cx_output)