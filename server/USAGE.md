# 高岸ERP API 服务

## Windows 一键启动

```powershell
cd server
python run.py
```

## 初始化数据库（首次或重置）

```powershell
cd server
rm gaoan_erp.db
python seed.py
```

## 测试 API

打开 http://localhost:8000/docs 查看 Swagger 文档。

测试登录:
```powershell
curl -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"admin123"}'
```

测试商品列表:
```powershell
$TOKEN = (curl -s -X POST http://localhost:8000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"admin123"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s "http://localhost:8000/api/products" -H "Authorization: Bearer $TOKEN"
```
