# -*- coding: utf-8 -*-
from pathlib import Path

file_path = Path(r"c:\Users\Administrator\Desktop\my-text\.trae\rules\rule-engine.md")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

rule = {
    "name": "",
    "core_functions": [],
    "execution_steps": [],
    "constraint_rules": [],
    "related_modules": []
}

current_section = None
section_content = []

section_map = {
    "核心功能": "core_functions",
    "执行步骤": "execution_steps",
    "约束规则": "constraint_rules",
    "关联模块": "related_modules"
}

for i, line in enumerate(lines):
    line = line.rstrip("\r\n")

    if line.startswith("# ") and current_section is None:
        rule["name"] = line[2:].strip()
        print(f"Line {i+1}: Set name = '{rule['name']}'")
        continue

    if line.startswith("## "):
        section_name = line[3:].strip()
        new_section = section_map.get(section_name)
        print(f"Line {i+1}: Found section '{section_name}' -> {new_section}")

        if current_section and section_content:
            print(f"  Processing previous section '{current_section}' with {len(section_content)} lines")
            if current_section == "related_modules":
                modules = []
                for l in section_content:
                    l = l.strip()
                    if l and not l.startswith("#"):
                        modules.extend([m.strip() for m in l.split("、") if m.strip()])
                rule[current_section] = modules
            else:
                items = []
                for l in section_content:
                    l = l.strip()
                    if l and not l.startswith("#") and not l.startswith("-"):
                        items.append(l)
                        print(f"    Added: {l[:30]}...")
                rule[current_section] = items

        current_section = new_section
        section_content = []
    else:
        if current_section:
            section_content.append(line)

if current_section and section_content:
    print(f"Processing final section '{current_section}' with {len(section_content)} lines")
    if current_section == "related_modules":
        modules = []
        for l in section_content:
            l = l.strip()
            if l and not l.startswith("#"):
                modules.extend([m.strip() for m in l.split("、") if m.strip()])
        rule[current_section] = modules
    else:
        items = []
        for l in section_content:
            l = l.strip()
            if l and not l.startswith("#") and not l.startswith("-"):
                items.append(l)
        rule[current_section] = items

print("\n=== Result ===")
print(f"Name: {rule['name']}")
print(f"Core functions: {len(rule['core_functions'])}")
for cf in rule['core_functions']:
    print(f"  - {cf[:50]}")
