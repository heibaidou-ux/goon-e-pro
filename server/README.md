# 高岸ERP API Server V1.0

## 技术栈

- **框架**: FastAPI (Python 3.14+)
- **数据库**: SQLite + SQLAlchemy (async)
- **认证**: JWT (python-jose)
- **文件处理**: Pillow (多尺寸缩略图)
- **ORM**: SQLAlchemy 2.0 (async)

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库并导入种子数据
python seed.py

# 3. 启动服务器
python run.py
# 或: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. 打开浏览器访问
# http://localhost:8000/docs   (Swagger API文档)
# http://localhost:8000/api/health (健康检查)
```

## 默认测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| staff | staff123 | 店员 |

## 项目结构

```
server/
├── main.py              # FastAPI 入口
├── config.py            # 配置文件
├── database.py          # 数据库连接
├── run.py               # 启动脚本
├── seed.py              # 种子数据初始化
├── requirements.txt      # 依赖清单
├── models/              # SQLAlchemy ORM 模型
│   ├── user.py          # 用户模型
│   ├── product.py       # 商品/分类/图片模型
│   ├── room.py          # 门店/房间/房间订单模型
│   └── order.py         # 商城订单模型
├── schemas/             # Pydantic 数据模型
│   ├── user.py
│   ├── product.py
│   └── order.py
├── routers/             # API 路由
│   ├── auth.py          # 认证 API
│   ├── products.py      # 商品管理 API (含图片上传)
│   ├── rooms.py         # 房间/订单 API
│   └── shop.py          # 商城订单 API
├── services/            # 业务逻辑
│   ├── auth_service.py  # JWT/密码服务
│   └── image_service.py # 图片处理服务
└── uploads/             # 上传文件存储
    └── products/        # 商品图片 (按ID分目录)
```

## API 端点

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 当前用户

### 商品管理
- `GET /api/products` - 商品列表 (分页/搜索/筛选)
- `GET /api/products/{id}` - 商品详情
- `POST /api/products` - 新增商品
- `PUT /api/products/{id}` - 编辑商品
- `DELETE /api/products/{id}` - 删除商品
- `GET /api/products/categories` - 分类列表
- `POST /api/products/categories` - 新增分类
- `POST /api/products/{id}/images` - 上传商品图片 (多尺寸缩略图自动生成)
- `DELETE /api/products/{id}/images/{img_id}` - 删除图片

### 房间管理
- `GET /api/stores` - 门店列表 (含房间)
- `GET /api/rooms` - 房间列表
- `GET /api/rooms/{id}` - 房间详情
- `GET /api/orders` - 订单列表 (需认证)
- `GET /api/orders/active` - 活跃订单
- `POST /api/orders` - 创建订单

### 商城
- `POST /api/shop/orders` - 创建商城订单
- `GET /api/shop/orders` - 订单列表 (需认证)
- `GET /api/shop/orders/{id}` - 订单详情

## 图片上传

商品图片上传后自动生成 4 种尺寸:
- `original/` - 原始图片
- `240/` - 240px 方形缩略图 (列表用)
- `480/` - 480px 中图 (分类浏览用)
- `800/` - 800px 大图 (详情页轮播用)

缩略图自动转换为 WebP 格式。
