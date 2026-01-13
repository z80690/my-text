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
ENV SUPABASE_JWT_SECRET=your_jwt_secret_here
ENV PORT=9000
ENV ENVIRONMENT=development
ENV LOG_LEVEL=INFO
ENV ACCESS_TOKEN_EXPIRY=3600
ENV REFRESH_TOKEN_EXPIRY=604800
ENV MIN_PASSWORD_LENGTH=8
ENV CORS_ORIGINS=http://localhost:3000,http://localhost:9000
ENV RATE_LIMIT_PER_MINUTE=60

# 运行测试脚本
CMD ["python", "test_connectivity.py"]