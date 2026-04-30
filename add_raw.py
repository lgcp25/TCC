import glob
import re

for tool_file in glob.glob("app/tools/*.py"):
    if "base_tool" in tool_file or "netcat" in tool_file: continue
    with open(tool_file, 'r') as f: content = f.read()
    if "raw_cmd=" in content: continue
    
    # regex to find def build_command(self, args...):
    match = re.search(r'(def build_command\(self, .*?)\):', content)
    if match:
        old_def = match.group(0)
        args_part = match.group(1)
        new_def = f"{args_part}, raw_cmd=None):\n        if raw_cmd:\n            import shlex\n            parts = shlex.split(raw_cmd)\n            if parts[0] == self.binary: return parts\n            return [self.binary] + parts\n"
        content = content.replace(old_def, new_def)
        with open(tool_file, 'w') as f: f.write(content)

for tab_file in glob.glob("app/ui/*_tab.py"):
    if "tool_tab" in tab_file or "netcat" in tab_file: continue
    with open(tab_file, 'r') as f: content = f.read()
    if "self.raw_cmd = " in content: continue
    
    field = """
        self.raw_cmd = ft.TextField(
            label="Comando Manual (Ignora os campos acima)",
            value="",
            **input_style
        )
"""
    content = content.replace("self.left_col.controls.extend([", field + "        self.left_col.controls.extend([")
    content = content.replace("])\n\n    def reset_fields", "    self.raw_cmd,\n        ])\n\n    def reset_fields")
    content = content.replace("self.app.page.update()", "self.raw_cmd.value = \"\"\n        self.app.page.update()")
    
    # Nmap
    if "verbose=self.verbose.value" in content:
        content = content.replace("verbose=self.verbose.value", "verbose=self.verbose.value,\n                raw_cmd=self.raw_cmd.value")
    # Sqlmap
    elif "data=self.data.value" in content:
        content = content.replace("data=self.data.value", "data=self.data.value,\n                raw_cmd=self.raw_cmd.value")
    # Nuclei
    elif "extra_params=self.extra_params.value" in content:
        content = content.replace("extra_params=self.extra_params.value", "extra_params=self.extra_params.value,\n                raw_cmd=self.raw_cmd.value")
        
    with open(tab_file, 'w') as f: f.write(content)

print("Done")
