# -*- coding: utf-8 -*-
from pathlib import Path

file_path = Path(r"c:\Users\Administrator\Desktop\my-text\.trae\rules\rule-engine.md")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("Lines analysis:")
for i, line in enumerate(lines[:15], 1):
    print(f"Line {i:2d}: [{line[:50]}]")
