import os
import glob

# Atualiza os arquivos python nas tools
tools_dir = "app/tools"
for tool_file in glob.glob(f"{tools_dir}/*.py"):
    if "base_tool" in tool_file or "netcat" in tool_file:
        continue
        
    with open(tool_file, 'r') as f:
        content = f.read()
        
    if "raw_cmd=" in content or "raw_cmd :" in content or "raw_cmd" in content.split("def build_command")[1].split(":")[0]:
        continue # Já tem
        
    # Encontra def build_command
    import re
    def_match = re.search(r"def build_command\(self, (.*?)\):", content)
    if not def_match:
        continue
    
    args = def_match.group(1)
    new_args = args + ", raw_cmd=None"
    
    # Adiciona a logica do raw_cmd logo após def build_command
    # Usando string replace
    old_def = f"def build_command(self, {args}):"
    new_def = f"def build_command(self, {args}, raw_cmd=None):\n        if raw_cmd:\n            import shlex\n            parts = shlex.split(raw_cmd)\n            if parts[0] == self.binary: return parts\n            return [self.binary] + parts\n"
    
    content = content.replace(old_def, new_def)
    
    with open(tool_file, 'w') as f:
        f.write(content)

# Atualiza as tabs
ui_dir = "app/ui"
for tab_file in glob.glob(f"{ui_dir}/*_tab.py"):
    if "tool_tab" in tab_file or "netcat" in tab_file:
        continue
        
    with open(tab_file, 'r') as f:
        content = f.read()
        
    if "self.raw_cmd = ft.TextField" in content:
        continue # Já tem
        
    # Adiciona o campo raw_cmd
    field_code = """
        self.raw_cmd = ft.TextField(
            label="Comando Manual (Ignora os campos acima)",
            value="",
            **input_style
        )
"""
    # Encontra self.left_col.controls.extend e injeta antes
    content = content.replace("self.left_col.controls.extend([", field_code + "\n        self.left_col.controls.extend([")
    
    # Encontra os campos na lista do extend e injeta self.raw_cmd,
    # Pode ser complexo. Melhor colocar no final:
    content = content.replace("])\n\n    def reset_fields", "    self.raw_cmd,\n        ])\n\n    def reset_fields")
    
    # No reset_fields
    content = content.replace("self.app.page.update()", "self.raw_cmd.value = \"\"\n        self.app.page.update()")
    
    # Na chamada do build_command
    if "extra_params=self.extra_params.value" in content:
        content = content.replace("extra_params=self.extra_params.value", "extra_params=self.extra_params.value,\n                raw_cmd=self.raw_cmd.value")
    
    with open(tab_file, 'w') as f:
        f.write(content)

print("Finalizado!")
