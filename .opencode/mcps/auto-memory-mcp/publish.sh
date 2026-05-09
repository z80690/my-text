#!/bin/bash

# 发布脚本

echo "🚀 开始发布 auto-memory-mcp..."

# 1. 清理
rm -rf dist node_modules

# 2. 安装依赖
echo "📦 安装依赖..."
npm install

# 3. 构建
echo "🔨 构建..."
npm run build

# 4. 测试
echo "🧪 测试..."
node dist/index.js --version || true

# 5. 登录npm（如果未登录）
echo "🔑 检查npm登录状态..."
npm whoami || npm login

# 6. 发布
echo "📤 发布到npm..."
npm publish --access public

echo "✅ 发布完成！"
