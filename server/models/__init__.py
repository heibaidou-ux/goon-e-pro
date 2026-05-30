# Register all models for auto-import
from models.user import User
from models.product import ProductCategory, Product, ProductImage
from models.room import Store, Room, RoomOrder
from models.order import ShopOrder, ShopOrderItem
from models.iot import IoTDevice, IoTAlert, IoTScene

all_models = [User, ProductCategory, Product, ProductImage, Store, Room, RoomOrder,
              ShopOrder, ShopOrderItem, IoTDevice, IoTAlert, IoTScene]
