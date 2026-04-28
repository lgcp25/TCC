from shared_imports import *

class Nikto(tb.Frame):
    def __init__(self, master):
        super.__init__(master)
# ============================================================
# ========================  ABA NIKTO  =========================
# ============================================================
def build_nikto_tab(self):
    tab = self.tabs["Nikto"]

    # ============================================================
    # FORMULÁRIO
    # ============================================================
    form = ttk.Labelframe(tab, text="Configuração do Nikto")
    form.pack(fill="x", padx=10, pady=10)

    ttk.Label(form, text="Host / URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.nikto_host = ttk.Entry(form, width=60)
    self.nikto_host.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(form, text="Porta (opcional):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    self.nikto_port = ttk.Entry(form, width=20)
    self.nikto_port.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    # SSL
    self.nikto_ssl = tk.BooleanVar()
    ttk.Checkbutton(form, text="Forçar SSL/HTTPS (-ssl)", variable=self.nikto_ssl).grid(
        row=2, column=1, sticky="w", padx=5
    )

    # ============================================================
    # OPÇÕES ESPECÍFICAS
    # ============================================================
    options = ttk.Labelframe(tab, text="Opções avançadas")
    options.pack(fill="x", padx=10, pady=10)

    ttk.Label(options, text="Tuning (ex: 123b):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.nikto_tuning = ttk.Entry(options, width=20)
    self.nikto_tuning.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(options, text="Plugins (ex: apacheusers):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    self.nikto_plugins = ttk.Entry(options, width=20)
    self.nikto_plugins.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    # User-Agent customizado
    ttk.Label(options, text="User-Agent (opcional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    self.nikto_ua = ttk.Entry(options, width=40)
    self.nikto_ua.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    # Saída JSON
    self.nikto_json = tk.BooleanVar()
    ttk.Checkbutton(options, text="Gerar JSON (-Format json)", variable=self.nikto_json).grid(
        row=3, column=1, sticky="w", padx=5
    )

    # Parâmetros extras
    ttk.Label(options, text="Parâmetros extras:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    self.nikto_extra = ttk.Entry(options, width=60)
    self.nikto_extra.grid(row=4, column=1, sticky="w", padx=5, pady=5)

    # ============================================================
    # OUTPUT
    # ============================================================
    self.nikto_output = tk.Text(tab, wrap="word", height=22)
    self.nikto_output.pack(fill="both", expand=True, padx=10, pady=10)

    # ============================================================
    # BOTÕES
    # ============================================================
    btns = ttk.Frame(tab)
    btns.pack(fill="x", pady=10)

    ttk.Button(btns, text="Gerar Comando", bootstyle="secondary",
                command=self.nikto_generate).pack(side="left", padx=5)

    ttk.Button(btns, text="Executar", bootstyle="success",
                command=self.nikto_execute).pack(side="left", padx=5)

    ttk.Button(btns, text="Cancelar", bootstyle="danger",
                command=self.cancel_process).pack(side="left", padx=5)

    ttk.Button(btns, text="Limpar", bootstyle="info",
                command=lambda: self.nikto_output.delete("1.0", "end")).pack(side="left", padx=5)


# ============================================================
# FUNÇÕES — NIKTO
# ============================================================
def nikto_generate(self):
    self.nikto_output.delete("1.0", "end")
    try:
        cmd = self.build_nikto_command()
        pretty = " ".join(shlex.quote(c) for c in cmd)
        self.nikto_output.insert("end", pretty + "\n")
    except Exception as e:
        self.nikto_output.insert("end", f"[ERRO] {e}\n")


def build_nikto_command(self):
    host = sanitize(self.nikto_host.get())
    if not valid_url(host):
        raise ValueError("Host inválido.")

    port = sanitize(self.nikto_port.get())
    tuning = sanitize(self.nikto_tuning.get())
    plugins = sanitize(self.nikto_plugins.get())
    user_agent = sanitize(self.nikto_ua.get())
    extra = sanitize(self.nikto_extra.get())

    cmd = ["nikto", "-h", host]

    if port:
        if not valid_port(port):
            raise ValueError("Porta inválida.")
        cmd += ["-p", port]

    if self.nikto_ssl.get():
        cmd.append("-ssl")

    if tuning:
        cmd += ["-Tuning", tuning]

    if plugins:
        cmd += ["-Plugins", plugins]

    if user_agent:
        cmd += ["-useragent", user_agent]

    if self.nikto_json.get():
        cmd += ["-Format", "json", "-output", "/work/output/nikto.json"]

    if extra:
        cmd += shlex.split(extra)

    return cmd


def nikto_execute(self):
    self.nikto_output.delete("1.0", "end")

    try:
        cmd = self.build_nikto_command()
    except Exception as e:
        self.nikto_output.insert("end", f"[ERRO] {e}\n")
        return

    self.run_docker("pentester", cmd, self.nikto_output)