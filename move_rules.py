import os
import shutil

base_path = r"c:\Users\Administrator\Desktop\my-text\.trae"

# 定义文件映射
mappings = {
    "rules/algorithm/algorithms.md": "algorithms",
    "rules/algorithm/data-structures.md": "algorithms",
    "rules/algorithm/cache-strategy.md": "cache",
    "rules/algorithm/rate-limiting.md": "rate_limiting",
    "rules/algorithm/ml-integration.md": "ml",
    "rules/skill/skill-integration.md": "skills",
    "rules/workflow/team-workflow.md": "workflows",
    "rules/workflow/tool-calling.md": "workflows",
    "rules/workflow/workflow-templates.md": "workflows",
}

print("开始移动规则文件...")
for src_rel, dest_dir in mappings.items():
    src = os.path.join(base_path, src_rel)
    dest = os.path.join(base_path, dest_dir, os.path.basename(src_rel))
    
    if os.path.exists(src):
        print(f"移动: {src_rel} -> {dest_dir}/")
        shutil.move(src, dest)
    else:
        print(f"跳过: {src_rel} (不存在)")

print("\n=== 完成 ===")