from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import io
import os
import uuid

from config import settings


class ImageService:
    """Product image processing: thumbnails, format conversion, local storage."""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    @staticmethod
    def _validate_image(content: bytes) -> Tuple[bool, str]:
        """Validate image format and size."""
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            return False, f"图片超过最大限制 {settings.max_upload_size_mb}MB"
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
            return True, "OK"
        except Exception:
            return False, "图片格式无效"

    @staticmethod
    def _ensure_dir(path: Path):
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _save_image(img: Image.Image, path: Path, quality: int = 85):
        """Save PIL image to path, converting to WebP when possible."""
        img.save(path, "WEBP" if path.suffix.lower() == ".webp" else None,
                 quality=quality, optimize=True)

    def process_product_image(self, content: bytes, product_id: str,
                              file_ext: str = ".jpg") -> dict:
        """
        Process uploaded product image:
        1. Validate
        2. Generate multi-size thumbnails
        3. Save to local storage
        Returns dict with URLs for each size.
        """
        valid, msg = self._validate_image(content)
        if not valid:
            raise ValueError(msg)

        img = Image.open(io.BytesIO(content))
        # Convert to RGB for WebP/JPEG consistency
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        image_id = str(uuid.uuid4())[:8]
        base_dir = Path(settings.upload_dir) / "products" / str(product_id)

        urls = {}

        # Save original
        orig_dir = base_dir / "original"
        self._ensure_dir(orig_dir)
        orig_name = f"{image_id}_original{file_ext}"
        orig_path = orig_dir / orig_name

        # Use Pillow to save original as well (consistent quality)
        img.save(orig_path, quality=92)
        urls["original"] = f"/uploads/products/{product_id}/original/{orig_name}"

        # Generate thumbnails
        for size in settings.thumbnail_sizes:
            thumb = img.copy()
            thumb.thumbnail((size, size), Image.LANCZOS)

            size_dir = base_dir / str(size)
            self._ensure_dir(size_dir)
            thumb_name = f"{image_id}_{size}.webp"
            thumb_path = size_dir / thumb_name

            # Center-crop to square for thumbnail
            if size <= 240:
                w, h = thumb.size
                min_dim = min(w, h)
                left = (w - min_dim) // 2
                top = (h - min_dim) // 2
                thumb = thumb.crop((left, top, left + min_dim, top + min_dim))

            self._save_image(thumb, thumb_path)
            urls[size] = f"/uploads/products/{product_id}/{size}/{thumb_name}"

        return urls

    @staticmethod
    def delete_product_images(product_id: str):
        """Delete all image files for a product."""
        base_dir = Path(settings.upload_dir) / "products" / str(product_id)
        if base_dir.exists():
            import shutil
            shutil.rmtree(base_dir)


image_service = ImageService()
