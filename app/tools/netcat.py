from shared_imports import *
import os

class Netcat(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
    # ============================================================
    # FUNÇÕES — NETCAT
    # ============================================================
    def select_file_netcat(self):
        p = filedialog.askopenfilename(initialdir="./work")
        if p:
            self.nc_file.delete(0, "end")
            self.nc_file.insert(0, p)

    def nc_generate(self):
        self.nc_output.delete("1.0", "end")
        try:
            cmd = self.build_nc_command()
            pretty = " ".join(shlex.quote(x) for x in cmd)
            self.nc_output.insert("end", pretty + "\n")
        except Exception as e:
            self.nc_output.insert("end", f"[ERRO] {e}\n")

    def build_nc_command(self):
        mode = self.nc_mode.get()
        host = sanitize(self.nc_host.get())
        port = sanitize(self.nc_port.get())
        file = sanitize(self.nc_file.get())
        raw = sanitize(self.nc_raw.get())

        # RAW COMMAND
        if mode == "Raw Command (avançado)":
            if not raw:
                raise ValueError("Digite um comando nc completo.")
            return ["bash", "-c", raw]

        # VALIDAÇÃO DE PORTA
        if not port.isdigit():
            raise ValueError("Porta inválida.")

        cmd = []

        # ===== CONNECT =====
        if mode.startswith("Conectar"):
            if not valid_url(host):
                raise ValueError("Host inválido.")
            cmd = ["nc", host, port]

        # ===== LISTENER =====
        elif mode.startswith("Escutar"):
            cmd = ["nc", "-lvnp", port]

        # ===== BANNER GRAB =====
        elif mode.startswith("Banner"):
            if not valid_url(host):
                raise ValueError("Host inválido.")
            cmd = ["bash", "-c", f"echo '' | nc {host} {port}"]

        # ===== SEND FILE =====
        elif mode.startswith("Enviar"):
            if not valid_url(host):
                raise ValueError("Host inválido.")
            if not os.path.exists(file):
                raise ValueError("Arquivo não encontrado.")
            cmd = ["bash", "-c", f"nc {host} {port} < '{file}'"]

        # ===== RECEIVE FILE =====
        elif mode.startswith("Receber"):
            if not os.path.exists(file):
                # Criar arquivo vazio
                open(file, "w").close()
            cmd = ["bash", "-c", f"nc -lvnp {port} > '{file}'"]

        return cmd

    def nc_execute(self):
        self.nc_output.delete("1.0", "end")

        try:
            cmd = self.build_nc_command()
        except Exception as e:
            self.nc_output.insert("end", f"[ERRO] {e}\n")
            return

        self.run_docker("pentester", cmd, self.nc_output)

    # ============================================================
    # ===============   FUNÇÕES AUXILIARES FINAIS   ===============
    # ============================================================

    def show_error(self, msg, widget=None):
        """
        Exibe erro e opcionalmente foca em um widget.
        """
        messagebox.showerror("Erro", msg)
        if widget:
            widget.focus()

    def safe_insert(self, widget, text):
        """
        Insere texto num widget de saída de forma segura.
        """
        widget.insert("end", text + "\n")
        widget.see("end")

    def clear_widget(self, widget):
        """
        Limpa um widget de texto.
        """
        widget.delete("1.0", "end")

    def run_background(self, func, *args):
        """
        Roda uma função em thread separada (caso precise no futuro).
        """
        th = threading.Thread(target=func, args=args, daemon=True)
        th.start()