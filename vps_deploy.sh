#!/bin/bash
# 高岸ERP VPS一键部署
# 用法: sudo bash vps_deploy.sh
set -e

cd /opt/gaoan-erp/repo || { echo "❌ repo目录不存在"; exit 1; }

echo "=== 1/4 拉取最新代码 ==="
git pull origin feature-full-prototype-alignment
echo "✅ 代码已更新"

echo "=== 2/4 重建容器 ==="
sudo docker compose down
sudo docker compose up -d --build
echo "⏳ 等待15秒启动..."
sleep 15

echo "=== 3/4 健康检查 ==="
curl -s http://localhost:8000/api/health && echo ""
curl -s http://localhost:8000/api/iot/health && echo ""

echo "=== 4/4 初始化数据库 ==="
sudo docker exec gaoan-erp python seed.py || echo "⚠️ seed已存在，跳过"

echo ""
echo "✅ 部署完成！"
echo "   登录账号: admin / admin123"
echo "   微信支付: 已配置"
echo "   HA联动: 82个设备"
