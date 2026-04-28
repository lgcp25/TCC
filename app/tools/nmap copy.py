
from shared_imports import *
class Nmap():
    def __init__(self, app):
        self.app = app
        
    def build(self):
        tab = self.app.tabs["Nmap"]

        # ============================================================
        # FORMULÁRIO SUPERIOR
        # ============================================================
        form = ttk.Labelframe(tab, text="Configuração do Scan")
        form.pack(fill="x", padx=10, pady=10)

        # Alvo
        ttk.Label(form, text="Alvo (IP / Host):").grid(row=0,
                                                    column=0, sticky="w", padx=5, pady=5)
        self.app.nmap_target = ttk.Entry(form, width=50)
        self.app.nmap_target.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Porta opcional
        ttk.Label(form, text="Porta (opcional):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.app.nmap_port = ttk.Entry(form, width=20)
        self.app.nmap_port.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # ============================================================
        # OPÇÕES DE SCAN
        # ============================================================
        frame_modes = ttk.Labelframe(tab, text="Modo de Varredura")
        frame_modes.pack(fill="x", padx=10, pady=10)

        self.app.nmap_mode = ttk.Combobox(
            frame_modes,
            width=55,
            state="readonly",
            values=[
                "Ver portas abertas (varre todas as portas, pode demorar)",
                "Scan portas comuns (top 1000)",
                "Scan porta específica (usar campo Porta)",
                "Varredura completa TCP com detecção de SO e versões (-p- -sS -sV -O)",
                "Scan agressivo (scripts default + OS + version) (-A)",
                "UDP scan (top 1000) (-sU)",
                "Usar scripts de vulnerabilidade (--script vuln)"
            ]
        )
        self.app.nmap_mode.grid(row=0, column=0, padx=5, pady=10)
        self.app.nmap_mode.current(0)

        # Verbose
        self.app.nmap_verbose = tk.BooleanVar()
        ttk.Checkbutton(frame_modes, text="Verbose (-v)", variable=self.app.nmap_verbose).grid(
            row=0, column=1, padx=10
        )

        # ============================================================
        # OUTPUT
        # ============================================================
        output_container = ttk.Frame(tab)
        output_container.pack(fill="both", expand=True, padx=10, pady=10)

        # lado esquerdo → OUTPUT
        left_frame = ttk.Labelframe(output_container, text="Resultado do Scan")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.app.nmap_output = tk.Text(left_frame, wrap="word", insertontime=0)
        self.app.nmap_output.pack(fill="both", expand=True)
        
        #Bloqueia entrada no terminal
        self.app.nmap_output.bind("<Key>", lambda e: "break")

        # lado direito → IA
        right_frame = ttk.Labelframe(output_container, text="Análise da IA")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.app.nmap_ai_output = tk.Text(right_frame, wrap="word", insertontime=0)
        self.app.nmap_ai_output.pack(fill="both", expand=True)
        
        #Bloqueia entrada no terminal IA
        self.app.nmap_ai_output.bind("<Key>", lambda e: "break")

        # ============================================================
        # BOTÕES
        # ============================================================
        btns = ttk.Frame(tab)
        btns.pack(fill="x", pady=10)

        ttk.Button(btns, text="Gerar Comando", bootstyle="secondary",
                command=self.nmap_generate).pack(side="left", padx=5)

        self.app.btn_execute = ttk.Button(
            btns,
            text="Executar",
            bootstyle="success",
            command=self.nmap_execute
            )
        self.app.btn_execute.pack(side="left", padx=5)

        self.app.btn_cancel = ttk.Button(
            btns,
            text="Cancelar",
            bootstyle="danger",
            command=self.app.cancel_process
        )
        self.app.btn_cancel.pack(side="left", padx=5)
        self.app.btn_cancel.config(state="disabled")

        ttk.Button(btns, text="Limpar", bootstyle="info",
                command=lambda: [self.app.nmap_output.delete("1.0", "end"),
                                 self.app.nmap_ai_output.delete("1.0", "end")]).pack(side="left", padx=5)

        # ============================================================
        # BOTÕES IA
        # ============================================================
        
        
    def nmap_generate(self):
        self.app.nmap_output.delete("1.0", "end")
        try:
            cmd = self.build_nmap_command()
            pretty = " ".join(shlex.quote(c) for c in cmd)
            self.app.nmap_output.insert("end", pretty + "\n")
        except Exception as e:
            self.app.nmap_output.insert("end", f"[ERRO] {e}\n")


    def build_nmap_command(self):
        target = sanitize(self.app.nmap_target.get())
        if not valid_url(target):
            raise ValueError("Alvo inválido.")

        mode = self.app.nmap_mode.get()
        port = sanitize(self.app.nmap_port.get())

        cmd = ["nmap"]

        if mode == "Ver portas abertas (varre todas as portas, pode demorar)":
            cmd += ["-p-", "--open", "-sV"]

        elif mode == "Scan portas comuns (top 1000)":
            cmd += ["-sT", "--top-ports", "1000", "-sV"]

        elif mode == "Scan porta específica (usar campo Porta)":
            if not valid_port(port):
                raise ValueError("Porta inválida.")
            cmd += ["-p", port, "-sV"]

        elif mode == "Varredura completa TCP com detecção de SO e versões (-p- -sS -sV -O)":
            cmd += ["-p-", "-sT", "-sV", "-O", "-T4"]

        elif mode == "Scan agressivo (scripts default + OS + version) (-A)":
            cmd += ["-A", "-T4"]

        elif mode == "UDP scan (top 1000) (-sU)":
            cmd += ["-sU", "--top-ports", "1000"]

        elif mode == "Usar scripts de vulnerabilidade (--script vuln)":
            cmd += ["-sV", "--script", "vuln"]

        # Verbose extra
        if self.app.nmap_verbose.get():
            cmd.append("-v")

        # Final: alvo
        cmd.append(target)

        return cmd

    def nmap_execute(self):
        self.app.nmap_output.delete("1.0", "end")
        self.app.nmap_ai_output.delete("1.0", "end")
        
        self.app.btn_execute.config(state="disabled")
        self.app.btn_cancel.config(state="normal")

        try:
            cmd = self.build_nmap_command()
        except Exception as e:
            self.app.nmap_output.insert("end", f"[ERRO] {e}\n")
            return
        
        self.app.current_output = self.app.nmap_output
        self.app.run_docker("pentester", cmd, self.app.nmap_output)
        
