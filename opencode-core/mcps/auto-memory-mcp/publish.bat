@echo off
chcp 65001

echo 🚀 开始发布 auto-memory-mcp...

:: 1. 清理
if exist dist rmdir /s /q dist
if exist node_modules rmdir /s /q node_modules

:: 2. 安装依赖
echo 📦 安装依赖...
npm install

:: 3. 构建
echo 🔨 构建...
npm run build

:: 4. 登录npm（如果未登录）
echo 🔑 检查npm登录状态...
npm whoami 2>nul || npm login

:: 5. 发布
echo 📤 发布到npm...
npm publish --access public

echo ✅ 发布完成！
pause
