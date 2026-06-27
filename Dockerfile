# 高岸ERP API Server — 生产Docker镜像
FROM python:3.12-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python依赖
COPY server/requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制全项目（prototype前端页面 + server后端）
COPY server/ ./server/
COPY prototype/ ./prototype/
COPY index.html .
COPY .nojekyll .

# 创建数据目录
RUN mkdir -p uploads logs

WORKDIR /app/server

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

EXPOSE 8000

# 生产启动（workers=1 兼容SQLite并发限制；生产推荐切PostgreSQL后改大workers数）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
