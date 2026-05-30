"""
Database seed script.
Reads mock JSON files from prototype/shared-mock/ and populates the database.
"""
import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, async_session_factory
from models.product import Product, ProductCategory
from models.room import Store, Room, RoomOrder
from models.user import User
from services.auth_service import hash_password

MOCK_DIR = Path(__file__).parent.parent / "prototype" / "shared-mock"


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

        # ── Categories ──
        categories = [
            {"name": "茶叶", "subcategories": ["绿茶", "红茶", "乌龙茶", "白茶", "普洱", "花茶"], "sort_order": 1},
            {"name": "茶具", "subcategories": ["茶壶", "茶杯", "茶盘", "茶道配件"], "sort_order": 2},
            {"name": "茶点", "subcategories": ["糕点", "坚果", "蜜饯"], "sort_order": 3},
            {"name": "套餐", "subcategories": ["双人套餐", "四人套餐", "商务套餐"], "sort_order": 4},
            {"name": "其他", "subcategories": ["水", "饮料", "其他"], "sort_order": 5},
        ]
        for c in categories:
            cat = ProductCategory(name=c["name"], subcategories=json.dumps(c["subcategories"], ensure_ascii=False),
                                  sort_order=c["sort_order"])
            db.add(cat)

        # ── Stores ──
        store = Store(
            store_id="YINGLONG",
            name="盈隆店",
            address="广州市天河区珠江新城华夏路28号盈隆大厦16层",
            phone="020-8888-8888",
        )
        db.add(store)

        # ── Rooms ──
        rooms_data = [
            {"room_id": "RM001", "name": "大茶室C", "type": "TeaRoom", "capacity": 6,
             "price_per_hour": 88, "price_per_half_hour": 48, "floor": "16F",
             "facilities": ["投影", "WiFi", "茶具", "空调"], "description": "宽敞大茶室，适合商务洽谈和小型聚会"},
            {"room_id": "RM002", "name": "中茶室A", "type": "TeaRoom", "capacity": 4,
             "price_per_hour": 68, "price_per_half_hour": 38, "floor": "16F",
             "facilities": ["WiFi", "茶具", "空调"], "description": "温馨中茶室，适合朋友小聚"},
            {"room_id": "RM003", "name": "中茶室B", "type": "TeaRoom", "capacity": 4,
             "price_per_hour": 68, "price_per_half_hour": 38, "floor": "16F",
             "facilities": ["WiFi", "茶具", "空调"], "description": "优雅中茶室，适合品茶休闲"},
            {"room_id": "RM004", "name": "VIP房", "type": "TeaRoom", "capacity": 8,
             "price_per_hour": 168, "price_per_half_hour": 88, "floor": "16F",
             "facilities": ["投影", "WiFi", "茶具", "空调", "音响", "独立洗手间"],
             "description": "豪华VIP房，配备顶级音响和独立洗手间"},
        ]
        for r in rooms_data:
            room = Room(
                room_id=r["room_id"], store_id="YINGLONG", name=r["name"],
                type=r["type"], capacity=r["capacity"],
                price_per_hour=r["price_per_hour"],
                price_per_half_hour=r["price_per_half_hour"],
                floor=r["floor"],
                facilities=json.dumps(r["facilities"], ensure_ascii=False),
                description=r["description"],
            )
            db.add(room)

        # ── Products (from shared-mock if available) ──
        products_file = MOCK_DIR / "orders.json"
        if products_file.exists():
            try:
                with open(products_file, encoding="utf-8") as f:
                    data = json.load(f)
                # Use orders data to seed some products
                products_seed = [
                    {"code": "TEA001", "name": "龙井绿茶", "category": "茶叶", "sub_category": "绿茶",
                     "spec": "250g/罐", "unit": "罐", "internal_price": 80, "retail_price": 128,
                     "is_food": True, "shelf_life": 720, "status": "上架",
                     "story": "产自杭州西湖核心产区，明前采摘，手工炒制。茶汤碧绿清澈，香气清幽持久，回甘悠长。",
                     "origin": "杭州西湖", "brewing_tips": '{"waterTemp":"80℃","steepTime":"2-3分钟","vessel":"玻璃杯","method":"上投法"}',
                     "lead_time": 7, "safe_stock": 10, "max_stock": 50, "current_stock": 30},
                    {"code": "TEA002", "name": "正山小种", "category": "茶叶", "sub_category": "红茶",
                     "spec": "200g/盒", "unit": "盒", "internal_price": 60, "retail_price": 98,
                     "is_food": True, "shelf_life": 1080, "status": "上架",
                     "story": "福建武夷山正山小种，传统烟熏工艺制作。松烟香浓郁，桂圆汤味醇厚甘甜。",
                     "origin": "福建武夷山", "brewing_tips": '{"waterTemp":"90℃","steepTime":"3-5分钟","vessel":"盖碗","method":"定点注水"}',
                     "lead_time": 5, "safe_stock": 10, "max_stock": 40, "current_stock": 25},
                    {"code": "TEA003", "name": "铁观音", "category": "茶叶", "sub_category": "乌龙茶",
                     "spec": "250g/罐", "unit": "罐", "internal_price": 90, "retail_price": 158,
                     "is_food": True, "shelf_life": 720, "status": "上架",
                     "story": "安溪铁观音，兰花香馥郁，观音韵明显。七泡有余香，乃乌龙茶中之极品。",
                     "origin": "福建安溪", "brewing_tips": '{"waterTemp":"95℃","steepTime":"1-2分钟","vessel":"紫砂壶","method":"高冲低斟"}',
                     "lead_time": 7, "safe_stock": 8, "max_stock": 40, "current_stock": 20},
                    {"code": "TEA004", "name": "普洱茶饼", "category": "茶叶", "sub_category": "普洱",
                     "spec": "357g/饼", "unit": "饼", "internal_price": 120, "retail_price": 198,
                     "is_food": True, "shelf_life": 9999, "status": "上架",
                     "story": "云南勐海古树原料，传统工艺石磨压制。越陈越香，可品饮可收藏。",
                     "origin": "云南勐海", "brewing_tips": '{"waterTemp":"100℃","steepTime":"10秒润茶","vessel":"紫砂壶","method":"沸水冲泡"}',
                     "lead_time": 10, "safe_stock": 5, "max_stock": 30, "current_stock": 15},
                    {"code": "CUP001", "name": "手工紫砂杯", "category": "茶具", "sub_category": "茶杯",
                     "spec": "1只", "unit": "只", "internal_price": 35, "retail_price": 68,
                     "is_food": False, "status": "上架",
                     "story": "宜兴原矿紫泥制作，手工雕刻梅花图案。透气性好，不烫手。",
                     "origin": "宜兴丁蜀", "lead_time": 14, "safe_stock": 20, "max_stock": 100, "current_stock": 50},
                    {"code": "FOOD001", "name": "绿豆糕", "category": "茶点", "sub_category": "糕点",
                     "spec": "200g/份", "unit": "份", "internal_price": 12, "retail_price": 25,
                     "is_food": True, "shelf_life": 30, "status": "上架",
                     "story": "传统手工制作，选用上等绿豆，口感细腻绵密，甜而不腻，配茶佳品。",
                     "origin": "广州", "lead_time": 3, "safe_stock": 30, "max_stock": 100, "current_stock": 60},
                    {"code": "PKG001", "name": "双人品茶套餐", "category": "套餐", "sub_category": "双人套餐",
                     "spec": "1份（2人）", "unit": "份", "internal_price": 68, "retail_price": 128,
                     "is_food": False, "status": "上架",
                     "story": "精选两款经典茶叶+两份茶点，适合两人共享品茶时光。",
                     "lead_time": 1, "safe_stock": 10, "max_stock": 50, "current_stock": 20},
                ]
                for p in products_seed:
                    product = Product(**p)
                    db.add(product)
            except Exception as e:
                print(f"Warning: could not seed products: {e}")

        await db.commit()
        print("[OK] DB seed complete!")
        print(f"   - Users: admin/admin123, staff/staff123")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Rooms: {len(rooms_data)}")
        print(f"   - Products: seeded")


if __name__ == "__main__":
    asyncio.run(seed())
