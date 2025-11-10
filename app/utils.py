from pathlib import Path
from django.conf import settings
import os

def _safe_name(s: str) -> str:
    # simple sanitizer for folder names
    return ''.join(c for c in s if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')

def generate_lote_qr_image(order_number: str, modelo: str, color: str, lote_number: int, total_lotes: int, lote_id: int):
    """
    Generate an image that contains:
      - NumeroOrden
      - Modelo-Color
      - "N numero de lote/ lotes totales" (e.g. "1/5")
      - a QR encoding the lote_id

    The image is saved under: BASE_DIR/QRs/NumeroOrden/Modelo-Color/lote_<idlote>.png
    Returns the absolute path to the saved image.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import qrcode
    except Exception:
        # required libraries not installed; silently skip and return None
        return None

    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    # build folder: QRs/NumeroOrden/Modelo-Color
    order_safe = _safe_name(str(order_number))
    model_color_safe = _safe_name(f"{modelo}-{color}")
    out_dir = base_dir / 'QRs' / order_safe / model_color_safe
    out_dir.mkdir(parents=True, exist_ok=True)

    # image layout
    width = 600
    height = 300
    bg_color = (255, 255, 255)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # fonts (fallback to default)
    try:
        font_large = ImageFont.truetype('arial.ttf', 28)
        font_small = ImageFont.truetype('arial.ttf', 18)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # left side text
    padding = 20
    x_text = padding
    y = padding
    draw.text((x_text, y), str(order_number), font=font_large, fill=(0, 0, 0))
    y += 40
    draw.text((x_text, y), f"{modelo}-{color}", font=font_small, fill=(0, 0, 0))
    y += 30
    draw.text((x_text, y), f"{lote_number}/{total_lotes}", font=font_small, fill=(0, 0, 0))

    # generate QR for lote_id
    qr_data = str(lote_id)
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

    # paste QR on right side
    qr_w, qr_h = qr_img.size
    qr_x = width - qr_w - padding
    qr_y = (height - qr_h) // 2
    img.paste(qr_img, (qr_x, qr_y))

    # save file
    # save file named only with the lote id (e.g. 123.png)
    filename = f"{lote_id}.png"
    out_path = out_dir / filename
    img.save(out_path, format='PNG')
    return str(out_path)
