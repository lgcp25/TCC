import glob
for file in glob.glob("app/ui/*_tab.py"):
    with open(file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "self.raw_cmd," in line:
            # Check previous line
            prev_line = lines[i-1]
            if not prev_line.rstrip().endswith(",") and not prev_line.strip() == "":
                lines[i-1] = prev_line.rstrip() + ",\n"
    with open(file, 'w') as f:
        f.writelines(lines)
