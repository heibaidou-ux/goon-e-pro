"""
创建¥0.01测试产品 — 在VPS上运行:
  cd /opt/gaoan-erp
  sudo docker cp server/create_test_product.py gaoan-erp:/app/server/
  sudo docker exec gaoan-erp python3 /app/server/create_test_product.py
"""
import asyncio, uuid
from database import async_session_factory
from models.product import Product
from sqlalchemy import select

async def main():
    async with async_session_factory() as s:
        r = await s.execute(select(Product).where(Product.code == 'TEST_TEA'))
        existing = r.scalar_one_or_none()
        if existing:
            existing.retailPrice = 0.01
            existing.basePrice = 0.01
            existing.marketPrice = 0.01
            existing.status = '上架'
            print(f'已更新: {existing.name} -> ¥0.01')
        else:
            p = Product(
                productId='TEST_TEA_' + uuid.uuid4().hex[:8],
                code='TEST_TEA',
                name='【测试专用】特惠茶品',
                spec='1份', unit='份',
                basePrice=0.01, retailPrice=0.01, marketPrice=0.01,
                isFood=True, status='上架', sortOrder=99,
                description='全流程验证专用商品，价格¥0.01'
            )
            s.add(p)
            print(f'已创建测试茶品 ¥0.01')
        await s.commit()

        # 验证
        r2 = await s.execute(select(Product).where(Product.code == 'TEST_TEA'))
        p2 = r2.scalar_one_or_none()
        print(f'验证成功: {p2.name} ¥{p2.retailPrice} status={p2.status}')

asyncio.run(main())
