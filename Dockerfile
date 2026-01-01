# 使用国内镜像源的Python 3.10
FROM docker.m.daocloud.io/library/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制requirements.txt并安装依赖
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY src/ .

# 腾讯云云函数要求监听9000端口
EXPOSE 9000


# 设置环境变量
ENV SUPABASE_URL=your_supabase_url_here
ENV SUPABASE_KEY=your_supabase_key_here

# 运行测试脚本
CMD ["python", "test_connectivity.py"]