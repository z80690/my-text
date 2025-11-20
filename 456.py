import os

# 1. 定义临时文件路径（当前工作目录下）
temp_file = "test_environment.txt"

try:
    # 2. 写入内容到临时文件
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("环境验证成功！此文件由测试脚本自动生成。\n如果看到此内容，说明Python文件读写功能正常。")
    print(f"✅ 文件 '{temp_file}' 生成并写入成功！")

    # 3. 读取临时文件内容
    with open(temp_file, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"✅ 文件 '{temp_file}' 读取成功！")
    print("文件内容如下：")
    print(content)

    # 4. 删除临时文件
    os.remove(temp_file)
    print(f"✅ 已清理临时文件 '{temp_file}'")

except Exception as e:
    print(f"❌ 发生错误：{e}")