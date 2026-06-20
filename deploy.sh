#!/bin/bash
# =========================================================
# 高岸ERP — 一键部署脚本
# 适用: Ubuntu 22.04+ / Debian 12+
# 用法: sudo bash deploy.sh
# =========================================================
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  高岸ERP 一键部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# ── 检查 root ──
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}请以 root 用户运行: sudo bash deploy.sh${NC}"
  exit 1
fi

# ── 配置区域（按需修改）──
ER_PORT="${ER_PORT:-8000}"           # ERP服务端口
ER_DOMAIN="${ER_DOMAIN:-}"           # 域名（留空则不配HTTPS）
ER_ADMIN_EMAIL="${ER_ADMIN_EMAIL:-}" # 管理员邮箱（用于证书申请）
ER_REPO="https://github.com/heibaidou-ux/alien-trader-v2.git"
ER_BRANCH="feature-full-prototype-alignment"
ER_DATA="/opt/gaoan-erp"

echo ""
echo -e "${YELLOW}部署配置:${NC}"
echo "  端口: $ER_PORT"
echo "  域名: ${ER_DOMAIN:-未配置}"
echo "  数据目录: $ER_DATA"
echo ""

# ── 1. 安装 Docker ──
if ! command -v docker &>/dev/null; then
  echo -e "${YELLOW}[1/6] 安装 Docker...${NC}"
  curl -fsSL https://get.docker.com | bash
  systemctl enable docker && systemctl start docker
else
  echo -e "${GREEN}[1/6] Docker 已安装${NC}"
fi

# ── 2. 安装 Docker Compose ──
if ! command -v docker-compose &>/dev/null; then
  echo -e "${YELLOW}[2/6] 安装 Docker Compose...${NC}"
  curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
else
  echo -e "${GREEN}[2/6] Docker Compose 已安装${NC}"
fi

# ── 3. 创建目录结构 ──
echo -e "${YELLOW}[3/6] 创建目录结构...${NC}"
mkdir -p "$ER_DATA/data" "$ER_DATA/backups" "$ER_DATA/logs" "$ER_DATA/uploads"

# ── 4. 克隆代码 ──
echo -e "${YELLOW}[4/6] 拉取代码...${NC}"
if [ -d "$ER_DATA/repo" ]; then
  cd "$ER_DATA/repo" && git pull origin "$ER_BRANCH"
else
  git clone --depth 1 -b "$ER_BRANCH" "$ER_REPO" "$ER_DATA/repo"
fi

# ── 5. 生成 .env ──
echo -e "${YELLOW}[5/6] 生成配置...${NC}"
SECRET_KEY=$(openssl rand -hex 32)
cat > "$ER_DATA/.env" <<EOF
DEBUG=false
SECRET_KEY=$SECRET_KEY
CORS_ORIGINS=["https://$ER_DOMAIN"]$( [ -z "$ER_DOMAIN" ] && echo ' || ["*"]')
HA_URL=http://192.168.2.65:8123
HA_TOKEN=
EOF

# ── 6. docker-compose.yml ──
echo -e "${YELLOW}[6/6] 启动服务...${NC}"
cat > "$ER_DATA/docker-compose.yml" <<EOF
version: "3.8"
services:
  erp:
    build: $ER_DATA/repo
    container_name: gaoan-erp
    restart: unless-stopped
    ports:
      - "$ER_PORT:8000"
    volumes:
      - $ER_DATA/data:/app/data
      - $ER_DATA/uploads:/app/uploads
      - $ER_DATA/logs:/app/logs
    environment:
      - DEBUG=false
      - SECRET_KEY=$SECRET_KEY
      - DATABASE_URL=sqlite+aiosqlite:///./data/gaoan_erp.db
      - CORS_ORIGINS=["*"]
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

  # ── 定时备份 ──
  backup:
    image: alpine:latest
    container_name: gaoan-erp-backup
    restart: unless-stopped
    volumes:
      - $ER_DATA/data:/data:ro
      - $ER_DATA/backups:/backups
    entrypoint: |
      sh -c "
      while true; do
        DATE=\$(date +%Y%m%d_%H%M%S)
        cp /data/gaoan_erp.db /backups/gaoan_erp_\$DATE.db
        gzip -f /backups/gaoan_erp_\$DATE.db
        find /backups -name '*.db.gz' -mtime +30 -delete
        sleep 86400
      done"
EOF

# ── 构建并启动 ──
cd "$ER_DATA"
docker-compose up -d --build

# ── 初始化数据库 ──
sleep 3
docker exec gaoan-erp python seed.py || true

# ── admin-web 构建 ──
cd "$ER_DATA/repo/prototype/admin-web"
docker run --rm -v "$(pwd):/app" -w /app node:20 sh -c "npm install && npm run build" 2>/dev/null || true
cp -r dist/* "$ER_DATA/repo/prototype/admin-web-dist/" 2>/dev/null || true

# ── 配HTTPS（如有域名）──
if [ -n "$ER_DOMAIN" ]; then
  # 安装Nginx + certbot
  apt-get update -qq && apt-get install -y -qq nginx certbot python3-certbot-nginx >/dev/null 2>&1

  # 配置反向代理
  cat > /etc/nginx/sites-available/gaoan-erp <<EOF
server {
    listen 80;
    server_name $ER_DOMAIN;
    return 301 https://\$server\$request_uri;
}
server {
    listen 443 ssl http2;
    server_name $ER_DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$ER_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
  ln -sf /etc/nginx/sites-available/gaoan-erp /etc/nginx/sites-enabled/
  nginx -t && systemctl reload nginx

  # 申请证书
  if [ -n "$ER_ADMIN_EMAIL" ]; then
    certbot --nginx -d "$ER_DOMAIN" --non-interactive --agree-tos -m "$ER_ADMIN_EMAIL" || true
    echo "0 3 * * * root certbot renew --quiet" > /etc/cron.d/certbot-renew
  fi
fi

# ── 完成 ──
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  高岸ERP 部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  访问地址: http://服务器IP:$ER_PORT"
echo "  管理后台: http://服务器IP:$ER_PORT/#/login"
echo "  账号: admin / admin123"
if [ -n "$ER_DOMAIN" ]; then
  echo "  HTTPS:   https://$ER_DOMAIN"
fi
echo ""
echo -e "${YELLOW}数据目录: $ER_DATA${NC}"
echo -e "${YELLOW}备份目录: $ER_DATA/backups${NC}"
echo ""
echo -e "${GREEN}如要配置HA IoT, 执行:${NC}"
echo "  docker exec -it gaoan-erp python -c \"from config import settings; print(settings.ha_url)\""
echo "  # 然后修改 .env 中的 HA_URL 和 HA_TOKEN"
echo ""
echo -e "${GREEN}常用命令:${NC}"
echo "  重启: docker-compose -f $ER_DATA/docker-compose.yml restart"
echo "  日志: docker logs -f gaoan-erp"
echo "  升级: cd $ER_DATA/repo && git pull && docker-compose -f $ER_DATA/docker-compose.yml up -d --build"
echo "  回滚: docker-compose -f $ER_DATA/docker-compose.yml down && docker-compose -f $ER_DATA/docker-compose.yml up -d"
echo ""
