from shared_imports import *

class Dirsearch(tb.Frame):
    def __init__(self, master):
        super.__init__(master)
# ============================================================
# ======================  ABA DIRSEARCH  ======================
# ============================================================
def build_dirsearch_tab(self):
    tab = self.tabs["Dirsearch"]

    # ============================================================
    # FORMULÁRIO
    # ============================================================
    form = ttk.Labelframe(tab, text="Configuração do Dirsearch")
    form.pack(fill="x", padx=10, pady=10)

    ttk.Label(form, text="URL alvo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.ds_target = ttk.Entry(form, width=60)
    self.ds_target.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Wordlist
    ttk.Label(form, text="Wordlist:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    self.ds_wordlist = ttk.Entry(form, width=50)
    self.ds_wordlist.grid(row=1, column=1, sticky="w", padx=5)
    ttk.Button(form, text="Selecionar", bootstyle="info",
                command=self.select_wordlist_dirsearch).grid(
        row=1, column=2, padx=5
    )

    # ============================================================
    # OPÇÕES AVANÇADAS
    # ============================================================
    adv = ttk.Labelframe(tab, text="Opções Avançadas")
    adv.pack(fill="x", padx=10, pady=10)

    # Extensões
    ttk.Label(adv, text="Extensões (.php,.txt):").grid(row=0, column=0, sticky="w", padx=5)
    self.ds_ext = ttk.Entry(adv, width=40)
    self.ds_ext.grid(row=0, column=1, sticky="w", padx=5)

    # Métodos HTTP
    ttk.Label(adv, text="Métodos (GET,POST):").grid(row=1, column=0, sticky="w", padx=5)
    self.ds_methods = ttk.Entry(adv, width=20)
    self.ds_methods.insert(0, "GET")
    self.ds_methods.grid(row=1, column=1, sticky="w", padx=5)

    # Recursion
    ttk.Label(adv, text="Nível de recursão:").grid(row=2, column=0, sticky="w", padx=5)
    self.ds_recursion = ttk.Entry(adv, width=10)
    self.ds_recursion.insert(0, "1")
    self.ds_recursion.grid(row=2, column=1, sticky="w", padx=5)

    # Forçar lowercase
    self.ds_lower = tk.BooleanVar()
    ttk.Checkbutton(adv, text="Forçar lowercase (--lowercase)", variable=self.ds_lower).grid(
        row=3, column=1, sticky="w"
    )

    # Excluir status
    ttk.Label(adv, text="Excluir status (ex: 404,403):").grid(row=4, column=0, sticky="w", padx=5)
    self.ds_exclude = ttk.Entry(adv, width=20)
    self.ds_exclude.grid(row=4, column=1, sticky="w", padx=5)

    # Threads
    ttk.Label(adv, text="Threads:").grid(row=5, column=0, sticky="w", padx=5)
    self.ds_threads = ttk.Entry(adv, width=10)
    self.ds_threads.insert(0, "30")
    self.ds_threads.grid(row=5, column=1, sticky="w", padx=5)

    # Timeout
    ttk.Label(adv, text="Timeout (s):").grid(row=6, column=0, sticky="w", padx=5)
    self.ds_timeout = ttk.Entry(adv, width=10)
    self.ds_timeout.insert(0, "10")
    self.ds_timeout.grid(row=6, column=1, sticky="w", padx=5)

    # Output JSON
    self.ds_json = tk.BooleanVar()
    ttk.Checkbutton(adv, text="Salvar JSON (--json-report)", variable=self.ds_json).grid(
        row=7, column=1, sticky="w", pady=5
    )

    # Parâmetros extras
    ttk.Label(adv, text="Extras:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
    self.ds_extra = ttk.Entry(adv, width=60)
    self.ds_extra.grid(row=8, column=1, sticky="w", padx=5, pady=5)

    # ============================================================
    # OUTPUT
    # ============================================================
    self.ds_output = tk.Text(tab, wrap="word", height=22)
    self.ds_output.pack(fill="both", expand=True, padx=10, pady=10)

    # ============================================================
    # BOTÕES
    # ============================================================
    btns = ttk.Frame(tab)
    btns.pack(fill="x", pady=10)

    ttk.Button(btns, text="Gerar Comando", bootstyle="secondary",
                command=self.ds_generate).pack(side="left", padx=5)

    ttk.Button(btns, text="Executar", bootstyle="success",
                command=self.ds_execute).pack(side="left", padx=5)

    ttk.Button(btns, text="Cancelar", bootstyle="danger",
                command=self.cancel_process).pack(side="left", padx=5)

    ttk.Button(btns, text="Limpar", bootstyle="info",
                command=lambda: self.ds_output.delete("1.0", "end")).pack(side="left", padx=5)


# ============================================================
# SELECT WORDLIST
# ============================================================
def select_wordlist_dirsearch(self):
    p = filedialog.askopenfilename(initialdir="./wordlists")
    if p:
        self.ds_wordlist.delete(0, "end")
        self.ds_wordlist.insert(0, p)

# ============================================================
# GERAR COMANDO
# ============================================================
def ds_generate(self):
    self.ds_output.delete("1.0", "end")
    try:
        cmd = self.build_dirsearch_command()
        pretty = " ".join(shlex.quote(c) for c in cmd)
        self.ds_output.insert("end", pretty + "\n")
    except Exception as e:
        self.ds_output.insert("end", f"[ERRO] {e}\n")


def build_dirsearch_command(self):
    target = sanitize(self.ds_target.get())
    wl = sanitize(self.ds_wordlist.get())

    if not valid_url(target):
        raise ValueError("URL inválida.")

    if not os.path.exists(wl):
        raise ValueError("Wordlist inválida.")

    cmd = ["dirsearch", "-u", target, "-w", wl]

    # Extensões
    ext = sanitize(self.ds_ext.get())
    if ext:
        cmd += ["-e", ext]

    # Métodos
    methods = sanitize(self.ds_methods.get())
    if methods:
        cmd += ["-m", methods]

    # Recursão
    recursion = sanitize(self.ds_recursion.get())
    if recursion.isdigit():
        cmd += ["--recursion-depth", recursion]

    # Lowercase
    if self.ds_lower.get():
        cmd.append("--lowercase")

    # Excluir status
    exclude = sanitize(self.ds_exclude.get())
    if exclude:
        cmd += ["--exclude-status", exclude]

    # Threads
    threads = sanitize(self.ds_threads.get())
    if threads.isdigit():
        cmd += ["-t", threads]

    # Timeout
    timeout = sanitize(self.ds_timeout.get())
    if timeout.isdigit():
        cmd += ["--timeout", timeout]

    # JSON
    if self.ds_json.get():
        cmd += ["--json-report", "/work/output/dirsearch.json"]

    # Extras
    extra = sanitize(self.ds_extra.get())
    if extra:
        cmd += shlex.split(extra)

    return cmd

# ============================================================
# EXECUTAR
# ============================================================
def ds_execute(self):
    self.ds_output.delete("1.0", "end")

    try:
        cmd = self.build_dirsearch_command()
    except Exception as e:
        self.ds_output.insert("end", f"[ERRO] {e}\n")
        return

    self.run_docker("pentester", cmd, self.ds_output)