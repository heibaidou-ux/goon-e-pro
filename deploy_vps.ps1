# 高岸ERP VPS部署脚本
# 用法: 在Claude Code对话框输入: ! powershell -ExecutionPolicy Bypass deploy_vps.ps1

$VPS = "106.55.183.146"
$USER = "root"
$PASS = "1g0oAhdU^jnUQoW6hD"

Write-Host "=== 1/6 拉取最新代码 ===" -ForegroundColor Green
plink -pw $PASS -batch ${USER}@${VPS} "cd /opt/gaoan-erp/repo && git pull origin feature-full-prototype-alignment" 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "❌ 拉取代码失败" -ForegroundColor Red; exit 1 }
Write-Host "✅ 代码拉取成功" -ForegroundColor Green

Write-Host "=== 2/6 停止旧容器 ===" -ForegroundColor Green
plink -pw $PASS -batch ${USER}@${VPS} "cd /opt/gaoan-erp/repo && sudo docker compose down" 2>&1

Write-Host "=== 3/6 重建并启动 ===" -ForegroundColor Green
plink -pw $PASS -batch ${USER}@${VPS} "cd /opt/gaoan-erp/repo && sudo docker compose up -d --build 2>&1" 2>&1

Write-Host "等待10秒让服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "=== 4/6 健康检查 ===" -ForegroundColor Green
$HEALTH = plink -pw $PASS -batch ${USER}@${VPS} "curl -s http://localhost:8000/api/health" 2>&1
Write-Host "健康检查: $HEALTH" -ForegroundColor Cyan

Write-Host "=== 5/6 配置微信支付和HA参数 ===" -ForegroundColor Green
$ENV_CONFIG = @'

# 微信支付
WECHAT_MCH_ID=1747166566
WECHAT_PAY_KEY=w8Kp3mX7zR9vQ2jL5nA4cF6tH1bY0eSd
WECHAT_CERT_PATH=/opt/gaoan-erp/certs/apiclient_key.pem
ERP_BASE_URL=https://erp.highbank.cn
HA_URL=http://192.168.2.65:8123
HA_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3MjUyYzFlMjVhYzg0MzQ4YWRhMGU3ZGQyNTM4MjVjNyIsImlhdCI6MTc4MDQ0NDQ5MywiZXhwIjoyMDk1ODA0NDkzfQ.5RaGsUHIlKfrSAUPc9A_sX60vM9826ac8QAk3Hfvdjc
DIRECT_485_HOST=127.0.0.1
DIRECT_485_PORT=7003
'@

# 先在 .env 中去掉旧的重叠行，再追加新配置
plink -pw $PASS -batch ${USER}@${VPS} @"
cd /opt/gaoan-erp
# 去掉可能存在的旧配置行
sed -i '/^WECHAT_/d' .env 2>/dev/null || true
sed -i '/^ERP_BASE_URL/d' .env 2>/dev/null || true
sed -i '/^HA_URL=/d' .env 2>/dev/null || true
sed -i '/^HA_TOKEN=/d' .env 2>/dev/null || true
sed -i '/^DIRECT_485_/d' .env 2>/dev/null || true
cat >> .env << 'ENVEOF'
$(echo "$ENV_CONFIG" | Select-String -NotMatch "^$")
ENVEOF
"@ 2>&1

Write-Host "✅ .env 配置完成" -ForegroundColor Green

Write-Host "=== 6/6 重启容器 ===" -ForegroundColor Green
plink -pw $PASS -batch ${USER}@${VPS} "cd /opt/gaoan-erp && sudo docker compose restart && sleep 3 && docker logs gaoan-erp --tail 10" 2>&1

Write-Host "=== ✅ 全部完成 ===" -ForegroundColor Green
Write-Host "验证命令:" -ForegroundColor Yellow
Write-Host "  curl https://erp.highbank.cn/api/health" -ForegroundColor Cyan
Write-Host "  curl https://erp.highbank.cn/api/iot/health" -ForegroundColor Cyan
