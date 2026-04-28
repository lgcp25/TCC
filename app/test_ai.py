from services.ai_analyzer import analyze_nmap


output = """
PORT   STATE SERVICE VERSION
80/tcp open  http Apache httpd 2.4.25
"""

print(analyze_nmap("Explique esse resultado", output))