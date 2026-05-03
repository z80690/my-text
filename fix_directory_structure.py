import os
import shutil

def fix_nested_trae():
    base_path = r"C:\Users\Administrator\Desktop\my-text\.trae"
    rules_path = os.path.join(base_path, "rules")
    
    # 查找嵌套的 .trae 目录
    nested_trae = os.path.join(rules_path, ".trae")
    
    if not os.path.exists(nested_trae):
        print("未找到嵌套的 .trae 目录")
        return
    
    print(f"找到嵌套目录: {nested_trae}")
    
    # 获取嵌套 .trae 下的内容
    nested_rules = os.path.join(nested_trae, "rules")
    
    if os.path.exists(nested_rules):
        # 移动嵌套 rules 下的所有内容到上层 rules
        for item in os.listdir(nested_rules):
            src_path = os.path.join(nested_rules, item)
            dst_path = os.path.join(rules_path, item)
            
            if os.path.exists(dst_path):
                # 如果目标已存在，需要处理冲突
                if os.path.isdir(dst_path):
                    # 合并目录
                    merge_dirs(src_path, dst_path)
                else:
                    # 文件冲突，添加后缀
                    name, ext = os.path.splitext(dst_path)
                    counter = 1
                    while os.path.exists(dst_path):
                        dst_path = f"{name}_{counter}{ext}"
                        counter += 1
                    shutil.move(src_path, dst_path)
                    print(f"移动文件 (重命名): {src_path} -> {dst_path}")
            else:
                shutil.move(src_path, dst_path)
                print(f"移动: {src_path} -> {dst_path}")
    
    # 删除空的嵌套目录
    if os.path.exists(nested_trae):
        shutil.rmtree(nested_trae)
        print(f"删除空目录: {nested_trae}")
    
    print("\n目录结构修复完成！")

def merge_dirs(src, dst):
    """合并两个目录"""
    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        
        if os.path.isdir(src_item):
            if not os.path.exists(dst_item):
                os.makedirs(dst_item)
            merge_dirs(src_item, dst_item)
        else:
            if os.path.exists(dst_item):
                name, ext = os.path.splitext(dst_item)
                counter = 1
                while os.path.exists(dst_item):
                    dst_item = f"{name}_{counter}{ext}"
                    counter += 1
            shutil.move(src_item, dst_item)
            print(f"移动文件 (合并): {src_item} -> {dst_item}")

if __name__ == "__main__":
    fix_nested_trae()