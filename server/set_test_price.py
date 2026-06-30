"""
在VPS上执行:
  sudo docker cp server/set_test_price.py gaoan-erp:/app/server/
  sudo docker exec gaoan-erp python3 /app/server/set_test_price.py
"""
import asyncio, uuid, json
from datetime import date
from database import async_session_factory
from models.store_dev import Room, RoomPricing
from sqlalchemy import select

async def main():
    async with async_session_factory() as s:
        # 1. 确保RM099房间存在
        r = await s.execute(select(Room).where(Room.roomId == 'RM099'))
        room = r.scalar_one_or_none()
        if not room:
            room = Room(
                roomId='RM099', roomCode='RM099',
                storeId='YINGLONG', name='测试房间',
                type='TeaRoom', capacity=4, floor='16F',
                description='全流程验证专用测试房间',
                facilities=json.dumps(['茶台','WiFi','空调'], ensure_ascii=False),
                status='Active'
            )
            s.add(room)
            await s.flush()
            print('创建测试房间: RM099')

        # 2. 添加¥0.01定价
        pricing = RoomPricing(
            pricingId='PRC_TEST_' + uuid.uuid4().hex[:6],
            roomId='RM099',
            basePrice=0.01,
            unit='PerHour',
            status='Active',
            effectiveDate=date.today()
        )
        s.add(pricing)

        # 3. 同时把测试茶品价格改为0.01
        from models.product import Product
        r2 = await s.execute(select(Product).where(Product.code == 'TEST_TEA'))
        tea = r2.scalar_one_or_none()
        if tea:
            tea.retailPrice = 0.01
            tea.basePrice = 0.01
            print('测试茶品价格已设为¥0.01')

        await s.commit()

        # 验证
        r3 = await s.execute(select(RoomPricing).where(RoomPricing.roomId == 'RM099'))
        p = r3.scalar_one_or_none()
        print(f'验证: RM099 定价 ¥{p.basePrice}/{p.unit}')

        r4 = await s.execute(select(Product).where(Product.code == 'TEST_TEA'))
        t = r4.scalar_one_or_none()
        if t:
            print(f'验证: {t.name} ¥{t.retailPrice}')

asyncio.run(main())
