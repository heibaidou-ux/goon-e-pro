#!/bin/bash
set -e
cd /opt/gaoan-erp
sudo docker compose down 2>/dev/null || true
# 修正DB路径：确保指向持久卷（/app/server/data/ 是 ./data 的挂载点）
sudo sed -i 's|DATABASE_URL=sqlite+aiosqlite:///./gaoan_erp.db|DATABASE_URL=sqlite+aiosqlite:///./data/gaoan_erp.db|' .env 2>/dev/null || true
sudo rm -f data/gaoan_erp.db
cat > docker-compose.yml << 'DEOF'
services:
  erp:
    build: /opt/gaoan-erp
    container_name: gaoan-erp
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/server/data    # DB持久化（与DATABASE_URL的data/路径对齐）
      - ./uploads:/app/server/uploads
      - ./logs:/app/server/logs
    env_file:
      - .env
    environment:
      - DEBUG=false
DEOF
sudo docker compose up -d --build
sleep 5
sudo docker exec gaoan-erp python seed.py || true
curl -s http://localhost:8000/api/health
echo ""
echo "=== DONE ==="
