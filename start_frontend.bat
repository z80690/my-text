@echo off
echo 🚀 启动前端服务器...
echo 请等待服务器启动，然后在浏览器中访问 http://localhost:8080/agents.html

cd frontend
python -m http.server 8080