import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
import subprocess
import threading
import shlex
from services.docker_runner import run_docker, cancel_process
import os
from services.ai_service import ensure_model
from tools.nmap import Nmap
from ui.nmap_tab import NmapTab

class PentesterApp(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")   # Material-like theme

        self.title("Pentester Suite — Ultimate Edition")
        self.geometry("1280x820")
        self.minsize(1100, 750)

        # Diretório de trabalho docker
        self.docker_dir = os.path.join(os.path.dirname(__file__), "docker")
        if not os.path.isdir(self.docker_dir):
            os.makedirs(self.docker_dir, exist_ok=True)

        # Controle de processos Docker
        self.current_proc = None
        self.proc_thread = None

        # Notebook principal (ABAS)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Dicionário para cada aba
        self.tabs = {}

        # Criar ABAS
        for tool in [
            "Nmap",
            "SQLmap",
            "Nuclei",
            "Nikto",
            "Gobuster",
            "Dirsearch",
            "Commix",
            "Netcat",
        ]:
            self.create_tab(tool)

        # Construir conteúdo de cada aba
        self.nmap_tool = Nmap(self)
        self.nmap_tool.build()
        
        #self.build_sqlmap_tab()
        #self.build_nuclei_tab()
        #self.build_nikto_tab()
        #self.build_gobuster_tab()
        #self.build_dirsearch_tab()
        #self.build_commix_tab()
        #self.build_netcat_tab()

    # ======================================================
    # Criação de uma aba genérica
    # ======================================================
    def create_tab(self, name):
        frame = ttk.Frame(self.notebook)
        self.tabs[name] = frame
        self.notebook.add(frame, text=name)

    def init_ai():
        ensure_model()
    
    def on_process_finish(self):
        self.after(0, self.finish_ui)

    def finish_ui(self):
        self.btn_execute.config(state="normal")
        self.btn_cancel.config(state="disabled")
        self.current_proc = None 
        
    def run_docker(self, container, cmd, output_widget):
        self.current_proc = run_docker(self, container, cmd, output_widget, on_finish= self.on_process_finish)
                
    def cancel_process(self):
        if not self.current_proc:
            if hasattr(self, "current_output"):
                self.current_output.insert("end", "\n[Nenhum processo sendo excutado]\n")
            return
        
        cancel_process(self)
        
        if hasattr(self, "current_output"):
            self.current_output.insert("end", "\n[Processo cancelado]\n") 
        
        
        self.current_proc = None
        
         
    threading.Thread(target=ensure_model, daemon=True).start()