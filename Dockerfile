# 使用官方Python 3.9的轻量级镜像作为基础
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制src目录下的所有文件到容器的/app目录
COPY src/ .

# 安装Python依赖（使用国内镜像加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置环境变量（可选，更推荐在运行容器时传入）
ENV SUPABASE_URL=your_supabase_url_here
ENV SUPABASE_KEY=your_supabase_key_here

# 指定容器启动时默认运行的命令
CMD ["python", "test_connectivity.py"]