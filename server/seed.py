"""
Database seed script.
Populates the database with initial mock data for development/testing.
"""
import sys
import json
import asyncio
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, async_session_factory
from models.supply_chain import Product, ProductCategory
from models.store_dev import Store, Room
from models.user import User
from services.auth_service import hash_password


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


async def seed():
    await init_db()
    async with async_session_factory() as db:
        # ── Users ──
        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),
            display_name="系统管理员",
            role="admin",
        )
        db.add(admin)

        staff = User(
            username="staff",
            hashed_password=hash_password("staff123"),
            display_name="店员小张",
            role="staff",
        )
        db.add(staff)
        await db.flush()

        # ── Categories (new model: storeId + camelCase) ──
        categories = [
            {"name": "茶叶", "sortOrder": 1},
            {"name": "茶具", "sortOrder": 2},
            {"name": "茶点", "sortOrder": 3},
            {"name": "套餐", "sortOrder": 4},
            {"name": "其他", "sortOrder": 5},
        ]
        for c in categories:
            cat = ProductCategory(
                categoryId=_gen_id(), storeId="", name=c["name"],
                sortOrder=c["sortOrder"],
            )
            db.add(cat)

        # ── Stores (new model: camelCase) ──
        store = Store(
            storeId="YINGLONG", storeCode="YL001",
            orgId="", name="盈隆店",
            address="广州市天河区珠江新城华夏路28号盈隆大厦16层",
            phone="020-8888-8888",
            type="Direct",
        )
        db.add(store)

        # ── Rooms (new model: camelCase) ──
        rooms_data = [
            {"roomId": "RM001", "name": "丰沙里", "type": "MeetingRoom", "capacity": 10,
             "floor": "16F", "description": "专业会议室，配备投影和会议设备"},
            {"roomId": "RM002", "name": "翡冷翠", "type": "TeaRoom", "capacity": 4,
             "floor": "16F", "description": "温馨中茶室，适合朋友小聚"},
            {"roomId": "RM003", "name": "布拉格", "type": "TeaRoom", "capacity": 4,
             "floor": "16F", "description": "优雅中茶室，适合品茶休闲"},
            {"roomId": "RM004", "name": "白沙瓦", "type": "TeaRoom", "capacity": 6,
             "floor": "16F", "description": "宽敞大茶室，适合商务洽谈和小型聚会"},
        ]
        for r in rooms_data:
            room = Room(
                roomId=r["roomId"], roomCode=r["roomId"],
                storeId="YINGLONG", name=r["name"],
                type=r["type"], capacity=r["capacity"],
                floor=r.get("floor"), description=r.get("description"),
                facilities=json.dumps(["投影", "WiFi", "茶具", "空调"], ensure_ascii=False),
            )
            db.add(room)

        # ── Products ──
        products_seed = [
            {"code": "TEA001", "name": "龙井绿茶", "brand": "", "spec": "250g/罐", "unit": "罐",
             "basePrice": 80, "retailPrice": 128, "marketPrice": 0,
             "isFood": True, "shelfLife": 720, "status": "上架", "sortOrder": 1,
             "story": "产自杭州西湖核心产区，明前采摘，手工炒制。茶汤碧绿清澈，香气清幽持久，回甘悠长。",
             "origin": "杭州西湖", "brewingTips": '{"waterTemp":"80℃","steepTime":"2-3分钟","vessel":"玻璃杯"}',
             "description": "明前龙井，品质上乘"},
            {"code": "TEA002", "name": "正山小种", "brand": "", "spec": "200g/盒", "unit": "盒",
             "basePrice": 60, "retailPrice": 98, "marketPrice": 0,
             "isFood": True, "shelfLife": 1080, "status": "上架", "sortOrder": 2,
             "story": "福建武夷山正山小种，传统烟熏工艺制作。松烟香浓郁，桂圆汤味醇厚甘甜。",
             "origin": "福建武夷山", "brewingTips": '{"waterTemp":"90℃","steepTime":"3-5分钟","vessel":"盖碗"}',
             "description": "传统烟熏正山小种"},
            {"code": "TEA003", "name": "铁观音", "brand": "", "spec": "250g/罐", "unit": "罐",
             "basePrice": 90, "retailPrice": 158, "marketPrice": 0,
             "isFood": True, "shelfLife": 720, "status": "上架", "sortOrder": 3,
             "story": "安溪铁观音，兰花香馥郁，观音韵明显。七泡有余香，乃乌龙茶中之极品。",
             "origin": "福建安溪", "brewingTips": '{"waterTemp":"95℃","steepTime":"1-2分钟","vessel":"紫砂壶"}',
             "description": "安溪铁观音，兰花香"},
            {"code": "TEA004", "name": "普洱茶饼", "brand": "", "spec": "357g/饼", "unit": "饼",
             "basePrice": 120, "retailPrice": 198, "marketPrice": 0,
             "isFood": True, "shelfLife": 9999, "status": "上架", "sortOrder": 4,
             "story": "云南勐海古树原料，传统工艺石磨压制。越陈越香，可品饮可收藏。",
             "origin": "云南勐海", "brewingTips": '{"waterTemp":"100℃","steepTime":"10秒润茶","vessel":"紫砂壶"}',
             "description": "勐海古树普洱"},
            {"code": "CUP001", "name": "手工紫砂杯", "brand": "", "spec": "1只", "unit": "只",
             "basePrice": 35, "retailPrice": 68, "marketPrice": 0,
             "isFood": False, "status": "上架", "sortOrder": 5,
             "story": "宜兴原矿紫泥制作，手工雕刻梅花图案。透气性好，不烫手。",
             "origin": "宜兴丁蜀", "description": "宜兴手工紫砂杯"},
            {"code": "FOOD001", "name": "绿豆糕", "brand": "", "spec": "200g/份", "unit": "份",
             "basePrice": 12, "retailPrice": 25, "marketPrice": 0,
             "isFood": True, "shelfLife": 30, "status": "上架", "sortOrder": 6,
             "story": "传统手工制作，选用上等绿豆，口感细腻绵密，甜而不腻，配茶佳品。",
             "origin": "广州", "description": "传统手工绿豆糕"},
            {"code": "PKG001", "name": "双人品茶套餐", "brand": "", "spec": "1份（2人）", "unit": "份",
             "basePrice": 68, "retailPrice": 128, "marketPrice": 0,
             "isFood": False, "status": "上架", "sortOrder": 7,
             "story": "精选两款经典茶叶+两份茶点，适合两人共享品茶时光。",
             "description": "双人品茶体验套餐"},
            {"code": "TEA005", "name": "白毫银针", "brand": "", "spec": "200g/盒", "unit": "盒",
             "basePrice": 150, "retailPrice": 228, "marketPrice": 0,
             "isFood": True, "shelfLife": 730, "status": "上架", "sortOrder": 8,
             "story": "福鼎高山产区，纯芽头制作。毫香蜜韵，茶汤杏黄透亮，回味甘甜。",
             "origin": "福建福鼎", "brewingTips": '{"waterTemp":"85℃","steepTime":"2-3分钟","vessel":"玻璃杯"}',
             "description": "福鼎白毫银针"},
            {"code": "TEA006", "name": "大红袍", "brand": "", "spec": "100g/罐", "unit": "罐",
             "basePrice": 180, "retailPrice": 298, "marketPrice": 0,
             "isFood": True, "shelfLife": 1080, "status": "上架", "sortOrder": 9,
             "story": "武夷岩茶之王，岩骨花香，七泡八泡有余香，回甘持久。",
             "origin": "福建武夷山", "brewingTips": '{"waterTemp":"100℃","steepTime":"1-2分钟","vessel":"紫砂壶"}',
             "description": "武夷岩茶大红袍"},
            {"code": "TEA007", "name": "小青柑", "brand": "", "spec": "250g/罐", "unit": "罐",
             "basePrice": 50, "retailPrice": 88, "marketPrice": 0,
             "isFood": True, "shelfLife": 730, "status": "上架", "sortOrder": 10,
             "story": "新会青柑+云南普洱，柑果清香与普洱醇厚完美融合，老少皆宜。",
             "origin": "广东新会", "brewingTips": '{"waterTemp":"100℃","steepTime":"整颗冲泡","vessel":"盖碗"}',
             "description": "新会小青柑普洱茶"},
            {"code": "FOOD002", "name": "桂花糕", "brand": "", "spec": "150g/份", "unit": "份",
             "basePrice": 15, "retailPrice": 28, "marketPrice": 0,
             "isFood": True, "shelfLife": 15, "status": "上架", "sortOrder": 11,
             "story": "选用新鲜桂花，搭配糯米粉蒸制，花香四溢，软糯香甜，配茶上品。",
             "origin": "广州", "description": "手工桂花糕"},
        ]
        for p in products_seed:
            product = Product(productId=_gen_id(), **p)
            db.add(product)

        await db.commit()
        print("[OK] DB seed complete!")
        print(f"   - Users: admin/admin123, staff/staff123")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Rooms: {len(rooms_data)}")
        print(f"   - Products: {len(products_seed)}")


if __name__ == "__main__":
    asyncio.run(seed())
