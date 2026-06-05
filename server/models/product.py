"""
Product models — re-exported from D05 supply_chain module.

This module previously defined standalone Product/ProductCategory/ProductImage
models. Those definitions have been consolidated into models/supply_chain.py
(D05 供应链域) to avoid duplicate table registrations.

All code should import from models.supply_chain directly:
    from models.supply_chain import Product, ProductCategory, ProductImage
"""
from models.supply_chain import Product, ProductCategory, ProductImage

__all__ = ["Product", "ProductCategory", "ProductImage"]
