from shared_imports import *

class Gobuster(tb.Frame):
    def __init__(self, master):
        super.__init__(master)
# ============================================================
# ======================  ABA GOBUSTER  =======================
# ============================================================
def build_gobuster_tab(self):
    tab = self.tabs["Gobuster"]

    # ============================================================
    # FORMULÁRIO
    # ============================================================
    form = ttk.Labelframe(tab, text="Configuração do Gobuster")
    form.pack(fill="x", padx=10, pady=10)

    # Target
    ttk.Label(form, text="URL / Host / Domínio:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.gb_target = ttk.Entry(form, width=60)
    self.gb_target.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Modo principal
    ttk.Label(form, text="Modo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    self.gb_mode = ttk.Combobox(
        form, state="readonly", width=20,
        values=["dir", "dns", "vhost", "fuzz"]
    )
    self.gb_mode.grid(row=1, column=1, sticky="w", padx=5)
    self.gb_mode.current(0)

    # ============================================================
    # WORDLIST
    # ============================================================
    wl_frame = ttk.Labelframe(tab, text="Wordlist")
    wl_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(wl_frame, text="Arquivo de wordlist:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.gb_wordlist = ttk.Entry(wl_frame, width=50)
    self.gb_wordlist.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    ttk.Button(wl_frame, text="Selecionar", bootstyle="info",
                command=self.select_wordlist_gobuster).grid(
                    row=0, column=2, padx=5
                )

    # ============================================================
    # OPÇÕES AVANÇADAS
    # ============================================================
    adv = ttk.Labelframe(tab, text="Opções avançadas")
    adv.pack(fill="x", padx=10, pady=10)

    ttk.Label(adv, text="Threads:").grid(row=0, column=0, sticky="w", padx=5)
    self.gb_threads = ttk.Entry(adv, width=10)
    self.gb_threads.insert(0, "50")
    self.gb_threads.grid(row=0, column=1, sticky="w", padx=5)

    ttk.Label(adv, text="Extensões (csv,php,txt):").grid(row=1, column=0, sticky="w", padx=5)
    self.gb_extensions = ttk.Entry(adv, width=30)
    self.gb_extensions.grid(row=1, column=1, sticky="w", padx=5)

    # Status codes
    ttk.Label(adv, text="Status válidos (ex: 200,204,301):").grid(row=2, column=0, sticky="w", padx=5)
    self.gb_status = ttk.Entry(adv, width=30)
    self.gb_status.grid(row=2, column=1, sticky="w", padx=5)

    # Follow redirects
    self.gb_follow = tk.BooleanVar()
    ttk.Checkbutton(adv, text="Seguir redirects (-r)", variable=self.gb_follow).grid(
        row=3, column=1, sticky="w", padx=5
    )

    # Timeout
    ttk.Label(adv, text="Timeout (s):").grid(row=4, column=0, sticky="w", padx=5)
    self.gb_timeout = ttk.Entry(adv, width=10)
    self.gb_timeout.insert(0, "10")
    self.gb_timeout.grid(row=4, column=1, sticky="w", padx=5)

    # Parâmetros extras
    ttk.Label(adv, text="Extras:").grid(row=5, column=0, sticky="w", padx=5)
    self.gb_extra = ttk.Entry(adv, width=60)
    self.gb_extra.grid(row=5, column=1, sticky="w", padx=5, pady=5)

    # ============================================================
    # OUTPUT
    # ============================================================
    self.gb_output = tk.Text(tab, wrap="word", height=22)
    self.gb_output.pack(fill="both", expand=True, padx=10, pady=10)

    # ============================================================
    # BOTÕES
    # ============================================================
    btns = ttk.Frame(tab)
    btns.pack(fill="x", pady=10)

    ttk.Button(btns, text="Gerar Comando", bootstyle="secondary",
                command=self.gb_generate).pack(side="left", padx=5)

    ttk.Button(btns, text="Executar", bootstyle="success",
                command=self.gb_execute).pack(side="left", padx=5)

    ttk.Button(btns, text="Cancelar", bootstyle="danger",
                command=self.cancel_process).pack(side="left", padx=5)

    ttk.Button(btns, text="Limpar", bootstyle="info",
                command=lambda: self.gb_output.delete("1.0", "end")).pack(side="left", padx=5)


# ============================================================
#  SELECT WORDLIST
# ============================================================
def select_wordlist_gobuster(self):
    p = filedialog.askopenfilename(initialdir="./wordlists")
    if p:
        self.gb_wordlist.delete(0, "end")
        self.gb_wordlist.insert(0, p)

# ============================================================
#  MONTAR COMANDO
# ============================================================
def gb_generate(self):
    self.gb_output.delete("1.0", "end")
    try:
        cmd = self.build_gobuster_command()
        pretty = " ".join(shlex.quote(c) for c in cmd)
        self.gb_output.insert("end", pretty + "\n")
    except Exception as e:
        self.gb_output.insert("end", f"[ERRO] {e}\n")


def build_gobuster_command(self):
    mode = self.gb_mode.get()
    target = sanitize(self.gb_target.get())
    wl = sanitize(self.gb_wordlist.get())

    if not os.path.exists(wl):
        raise ValueError("Wordlist inválida.")

    cmd = ["gobuster", mode]

    if mode == "dir":
        if not valid_url(target):
            raise ValueError("URL inválida.")
        cmd += ["-u", target]

        ext = sanitize(self.gb_extensions.get())
        if ext:
            cmd += ["-x", ext]

    elif mode == "dns":
        cmd += ["-d", target]

    elif mode == "vhost":
        cmd += ["-u", target]

    elif mode == "fuzz":
        if "{FUZ}" not in target and "{GOBUSTER}" not in target:
            raise ValueError("URL para fuzz precisa conter {GOBUSTER} ou {FUZ}.")
        cmd += ["-u", target]

    # Wordlist
    cmd += ["-w", wl]

    # Threads
    cmd += ["-t", sanitize(self.gb_threads.get())]

    # Status
    status = sanitize(self.gb_status.get())
    if status:
        cmd += ["-s", status]

    # Timeout
    timeout = sanitize(self.gb_timeout.get())
    if timeout:
        cmd += ["-to", timeout]

    # Follow redirects
    if self.gb_follow.get():
        cmd.append("-r")

    # Extras
    extra = sanitize(self.gb_extra.get())
    if extra:
        cmd += shlex.split(extra)

    return cmd

# ============================================================
#  EXECUTAR
# ============================================================
def gb_execute(self):
    self.gb_output.delete("1.0", "end")
    try:
        cmd = self.build_gobuster_command()
    except Exception as e:
        self.gb_output.insert("end", f"[ERRO] {e}\n")
        return

    self.run_docker("pentester", cmd, self.gb_output)