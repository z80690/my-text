# 使用官方Python 3.9的轻量级镜像作为基础
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器的/app目录
# 注意：这需要您将源代码（如test_connectivity.py）和requirements.txt放在与Dockerfile同级的目录
COPY . .

# 安装Python依赖（使用国内镜像加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 设置环境变量（可选，更推荐在运行容器时传入）
# ENV SUPABASE_URL=your_url
# ENV SUPABASE_KEY=your_key

# 指定容器启动时默认运行的命令
# 请将`your_script.py`替换为您实际的入口Python脚本文件名
CMD ["python", "test_connectivity.py"]