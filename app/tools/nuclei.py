from shared_imports import *

class Nuclei(tb.Frame):
    def __init__(self, master):
        super.__init__(master)
# ============================================================
# =======================  ABA NUCLEI  ========================
# ============================================================
def build_nuclei_tab(self):
    tab = self.tabs["Nuclei"]

    # ============================================================
    # FORMULÁRIO
    # ============================================================
    form = ttk.Labelframe(tab, text="Configuração do Nuclei")
    form.pack(fill="x", padx=10, pady=10)

    # Alvo
    ttk.Label(form, text="URL / Host:").grid(row=0,
                                             column=0, sticky="w", padx=5, pady=5)
    self.nuclei_target = ttk.Entry(form, width=60)
    self.nuclei_target.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Parâmetro
    ttk.Label(form, text="Parâmetro extra (opcional):").grid(
        row=1, column=0, sticky="w", padx=5, pady=5
    )
    self.nuclei_param = ttk.Entry(form, width=40)
    self.nuclei_param.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    mode_box = ttk.Labelframe(tab, text="Modo de Execução")
    mode_box.pack(fill="x", padx=10, pady=10)

    self.nuclei_mode = ttk.Combobox(
        mode_box,
        width=55,
        state="readonly",
        values=[
            "Scan alvo (-u)",
            "Scan lista de alvos (-l)",
            "Atualizar templates (-update-templates)",
            "Scan com templates locais (-t)",
            "Salvar saída JSON (-json)",
            "Scan verbose (-v)"
        ]
    )
    self.nuclei_mode.grid(row=0, column=0, padx=5, pady=10)
    self.nuclei_mode.current(0)

    # Aviso útil
    ttk.Label(
        mode_box,
        text="Templates em: /opt/nuclei-templates\nTargets.txt em: /work/targets.txt",
        foreground="gray"
    ).grid(row=1, column=0, sticky="w", padx=5)

    # ============================================================
    # OUTPUT
    # ============================================================
    self.nuclei_output = tk.Text(tab, wrap="word", height=22)
    self.nuclei_output.pack(fill="both", expand=True, padx=10, pady=10)

    # ============================================================
    # BOTÕES
    # ============================================================
    btns = ttk.Frame(tab)
    btns.pack(fill="x", pady=10)

    ttk.Button(btns, text="Gerar Comando", bootstyle="secondary",
               command=self.nuclei_generate).pack(side="left", padx=5)

    ttk.Button(btns, text="Executar", bootstyle="success",
               command=self.nuclei_execute).pack(side="left", padx=5)

    ttk.Button(btns, text="Cancelar", bootstyle="danger",
               command=self.cancel_process).pack(side="left", padx=5)

    ttk.Button(btns, text="Limpar", bootstyle="info",
               command=lambda: self.nuclei_output.delete("1.0", "end")).pack(side="left", padx=5)

# ============================================================
# FUNÇÕES — NUCLEI
# ============================================================
def nuclei_generate(self):
    self.nuclei_output.delete("1.0", "end")
    try:
        cmd = self.build_nuclei_command()
        pretty = " ".join(shlex.quote(c) for c in cmd)
        self.nuclei_output.insert("end", pretty + "\n")
    except Exception as e:
        self.nuclei_output.insert("end", f"[ERRO] {e}\n")

def build_nuclei_command(self):
    mode = self.nuclei_mode.get()
    target = sanitize(self.nuclei_target.get())
    param = sanitize(self.nuclei_param.get())

    cmd = ["nuclei"]

    if mode == "Scan alvo (-u)":
        if not valid_url(target):
            raise ValueError("Alvo inválido.")
        cmd += ["-u", target]

    elif mode == "Scan lista de alvos (-l)":
        cmd += ["-l", "/work/targets.txt"]

    elif mode == "Atualizar templates (-update-templates)":
        cmd += ["-update-templates"]

    elif mode == "Scan com templates locais (-t)":
        if not valid_url(target):
           raise ValueError("Alvo inválido.")
        cmd += ["-u", target, "-t", "/opt/nuclei-templates"]

    elif mode == "Salvar saída JSON (-json)":
        if not valid_url(target):
            raise ValueError("Alvo inválido.")
        cmd += ["-u", target, "-json", "/work/output/result.json"]

    elif mode == "Scan verbose (-v)":
        if not valid_url(target):
            raise ValueError("Alvo inválido.")
        cmd += ["-u", target, "-v"]

    # Param extra
    if param:
        cmd += shlex.split(param)

    return cmd

def nuclei_execute(self):
    self.nuclei_output.delete("1.0", "end")

    try:
        cmd = self.build_nuclei_command()
    except Exception as e:
        self.nuclei_output.insert("end", f"[ERRO] {e}\n")
        return

    self.run_docker("pentester", cmd, self.nuclei_output)
