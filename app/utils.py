from pathlib import Path
from django.conf import settings
import os
import shutil

LABEL_WIDTH_MM = 110
LABEL_HEIGHT_MM = 50
LABEL_DPI = 300


def _mm_to_px(mm: float, dpi: int = LABEL_DPI) -> int:
    # 1 inch = 25.4 mm
    return max(1, int(round((float(mm) / 25.4) * int(dpi))))


def _label_size_px():
    return _mm_to_px(LABEL_WIDTH_MM), _mm_to_px(LABEL_HEIGHT_MM)

def _safe_name(s: str) -> str:
    # simple sanitizer for folder names
    return ''.join(c for c in s if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')


def build_prefixed_qr_value(prefix: str, entity_id) -> str:
    """Build prefixed QR values like E123 or L456."""
    pref = str(prefix or '').strip().upper()
    if pref not in ('E', 'L'):
        raise ValueError('El prefijo QR debe ser E o L.')

    entity_id_str = str(entity_id or '').strip()
    if not entity_id_str.isdigit():
        raise ValueError('El ID del QR debe ser numerico.')

    return f"{pref}{entity_id_str}"


def parse_prefixed_qr_value(raw_value: str):
    """
    Parse QR values in format E123/L456.
    Also accepts legacy numeric-only values for backward compatibility.

    Returns tuple: (prefix, parsed_id)
      - prefix is 'E', 'L' or None for legacy values
      - parsed_id is int
    """
    value = str(raw_value or '').strip().upper()
    if not value:
        raise ValueError('El QR esta vacio.')

    if value.isdigit():
        return None, int(value)

    prefix = value[:1]
    suffix = value[1:].strip()

    if suffix.startswith(':') or suffix.startswith('-'):
        suffix = suffix[1:].strip()

    if prefix not in ('E', 'L'):
        raise ValueError('El QR debe iniciar con E (empleado) o L (lote).')

    if not suffix.isdigit():
        raise ValueError('El QR no contiene un ID valido.')

    return prefix, int(suffix)


def parse_qr_id_for_prefix(raw_value: str, expected_prefix: str) -> int:
    """Validate expected prefix and return parsed numeric id."""
    expected = str(expected_prefix or '').strip().upper()
    if expected not in ('E', 'L'):
        raise ValueError('Prefijo esperado invalido.')

    prefix, parsed_id = parse_prefixed_qr_value(raw_value)
    if prefix and prefix != expected:
        label = 'empleado' if expected == 'E' else 'lote'
        raise ValueError(f'Se esperaba un QR de {label}.')

    return parsed_id


def _overlay_logo_on_qr(qr_img, base_dir: Path):
    """
    Overlay Trex logo in the center of the QR while keeping scan reliability.
    Returns the original QR image if logo is unavailable or an error occurs.
    """
    try:
        from PIL import Image, ImageOps

        logo_candidates = [
            base_dir / 'app' / 'static' / 'images' / 'LOGO_TREX.png',
            base_dir / 'app' / 'static' / 'images' / 'LOGO_TREX.jpg',
            base_dir / 'app' / 'static' / 'images' / 'icono.png',
        ]

        logo_path = next((p for p in logo_candidates if p.exists()), None)
        if not logo_path:
            return qr_img

        qr_rgba = qr_img.convert('RGBA')
        qr_w, qr_h = qr_rgba.size
        logo_size = int(min(qr_w, qr_h) * 0.18)
        if logo_size <= 0:
            return qr_img

        logo = Image.open(logo_path).convert('RGBA')
        if hasattr(Image, 'Resampling'):
            logo = ImageOps.contain(logo, (logo_size, logo_size), Image.Resampling.LANCZOS)
        else:
            logo = ImageOps.contain(logo, (logo_size, logo_size), Image.LANCZOS)

        # Add a white safety background around the logo to preserve QR contrast.
        pad = max(2, int(logo_size * 0.12))
        badge_side = max(logo.size) + (pad * 2)
        badge = Image.new('RGBA', (badge_side, badge_side), (255, 255, 255, 255))
        lx = (badge_side - logo.size[0]) // 2
        ly = (badge_side - logo.size[1]) // 2
        badge.paste(logo, (lx, ly), logo)

        pos_x = (qr_w - badge_side) // 2
        pos_y = (qr_h - badge_side) // 2
        qr_rgba.paste(badge, (pos_x, pos_y), badge)
        return qr_rgba.convert('RGB')
    except Exception:
        return qr_img

def delete_orden_qr_folder(order_number: str):
    """
    Delete entire QR folder for an order.
    
    Removes folder: BASE_DIR/QRs/NumeroOrden/
    Returns True if deletion was successful, False otherwise.
    """
    try:
        base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
        # build folder path: QRs/NumeroOrden
        order_safe = _safe_name(str(order_number))
        qr_dir = base_dir / 'QRs' / order_safe
        
        print(f"Intentando eliminar carpeta: {qr_dir}")
        
        # delete entire directory if it exists
        if qr_dir.exists():
            print(f"Carpeta existe: {qr_dir}")
            shutil.rmtree(qr_dir)
            print(f"Carpeta eliminada exitosamente: {qr_dir}")
            return True
        else:
            print(f"Carpeta no encontrada: {qr_dir}")
            # Listar lo que hay en QRs si existe
            qrs_dir = base_dir / 'QRs'
            if qrs_dir.exists():
                print(f"Contenido de {qrs_dir}: {list(qrs_dir.iterdir())}")
        return True
    except Exception as e:
        # log error but don't fail the operation
        print(f"Error deleting order QR folder: {e}")
        import traceback
        traceback.print_exc()
        return False

def delete_lote_qr_images(order_number: str, color: str, folio: str = ''):
    """
    Delete entire QR folder for a specific pedido (order/folio/color combination).
    
    Removes folder: BASE_DIR/QRs/NumeroOrden/Folio-Color/ OR Modelo-Color
    Returns True if deletion was successful, False otherwise.
    """
    try:
        base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
        order_safe = _safe_name(str(order_number))
        order_dir = base_dir / 'QRs' / 'Ordenes' / order_safe
        
        print(f"Buscando carpetas QR para eliminar en: {order_dir}")
        print(f"Criterios: folio={folio}, color={color}")
        
        if not order_dir.exists():
            print(f"Directorio de orden no existe: {order_dir}")
            return True
        
        # Buscar todas las subcarpetas y eliminar las que contengan el color
        deleted_any = False
        try:
            for subfolder in order_dir.iterdir():
                if subfolder.is_dir():
                    folder_name = subfolder.name
                    print(f"Revisando carpeta: {folder_name}")
                    
                    # Coincidir si el nombre contiene el color (sin sensibilidad a mayúsculas)
                    if color.lower() in folder_name.lower():
                        print(f"Coincidencia encontrada! Eliminando: {subfolder}")
                        shutil.rmtree(subfolder)
                        print(f"Carpeta eliminada: {subfolder}")
                        deleted_any = True
        except Exception as e:
            print(f"Error iterando subcarpetas: {e}")
        
        if deleted_any:
            print(f"Se eliminaron carpetas QR exitosamente")
        else:
            print(f"No se encontraron carpetas que coincidan con color={color}")
        
        return True
    except Exception as e:
        print(f"Error deleting QR folder: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_lote_qr_image(lote_obj, lote_number: int, total_lotes: int):
    """
    Generate an image that contains:
      - Modelo (large)
      - Folio
      - Cantidad de chinelas
      - Talla
      - Máquina tejido
      - Turno/Operador
      - Color
      - Máquina plancha
      - QR encoding the lote_id

    The image is saved under: BASE_DIR/QRs/NumeroOrden/Folio-Color/lote_<idlote>.png
    Returns the absolute path to the saved image.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import qrcode
    except Exception:
        return None

    pedido = lote_obj.idpedido
    modelo = pedido.idmodelo
    orden = pedido.idordenpedido
    
    model_str = modelo.modelo
    folio_str = modelo.folio
    color_str = pedido.color
    cantidad_str = str(lote_obj.cantidad)
    talla_str = str(pedido.talla)
    
    order_num = orden.numeroorden
    lote_id = lote_obj.idlote

    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    # build folder: QRs/NumeroOrden/Folio-Color
    order_safe = _safe_name(str(order_num))
    folio_color_safe = _safe_name(f"{folio_str}-{color_str}")
    out_dir = base_dir / 'QRs' / 'Ordenes' / order_safe / folio_color_safe
    out_dir.mkdir(parents=True, exist_ok=True)

    width, height = _label_size_px()
    bg_color = (255, 255, 255)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # fonts (fallback to default)
    try:
        font_xlarge = ImageFont.truetype('arialbd.ttf', 70)
        font_large = ImageFont.truetype('arial.ttf', 50)
        font_small = ImageFont.truetype('arial.ttf', 40)
    except Exception:
        font_xlarge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Layout: independent margins so text can move right without shrinking the QR.
    left_margin = 190
    qr_padding = 25
    x_text = left_margin
    y = 80
    
    # MODELO - Large at top
    draw.text((x_text, y), f"{order_num}", font=font_xlarge, fill=(0, 0, 0))
    y += 78
    
    # Folio and Cantidad
    draw.text((x_text, y),f"Modelo: {folio_str:<15}", font=font_small, fill=(0, 0, 0))
    y += 52
    
    draw.text((x_text, y),f"Cant. chinelas: {cantidad_str}", font=font_small, fill=(0, 0, 0))
    y += 52
    
    # Nombre modelo
    draw.text((x_text, y), f"{model_str}", font=font_small, fill=(0, 0, 0))
    y += 52
    
    # Talla, Maq tejido, Turno
    draw.text((x_text, y), f"Talla: {talla_str}", font=font_small, fill=(0, 0, 0))
    y += 52
    
    # Color, Operador
    draw.text((x_text, y), f"Color: {color_str:<25}", font=font_small, fill=(0, 0, 0))
    y += 52
    
    # Lote info
    draw.text((x_text, y), f"Lote: {lote_number}/{total_lotes}", font=font_large, fill=(0, 0, 0))

    # generate QR for lote_id with prefixed format (L{id})
    qr_data = build_prefixed_qr_value('L', lote_id)
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

    # Keep lote QR size aligned with employee QR cards.
    target_qr_side = min(height - (qr_padding * 2), int(width * 0.42))
    if hasattr(Image, 'Resampling'):
        qr_img = qr_img.resize((target_qr_side, target_qr_side), Image.Resampling.NEAREST)
    else:
        qr_img = qr_img.resize((target_qr_side, target_qr_side), Image.NEAREST)

    qr_img = _overlay_logo_on_qr(qr_img, base_dir)

    # paste QR on right side
    qr_w, qr_h = qr_img.size
    qr_x = width - qr_w - qr_padding
    qr_y = (height - qr_h) // 2
    img.paste(qr_img, (qr_x, qr_y))

    # save file
    filename = f"lote_{lote_number}.png"
    out_path = out_dir / filename
    img.save(out_path, format='PNG', dpi=(LABEL_DPI, LABEL_DPI))
    return str(out_path)


def get_empleado_qr_folder(area: str):
    """
    Return absolute path for employee QR folder.
    Folder pattern: BASE_DIR/QRs/Empleados/Area
    """
    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    area_safe = _safe_name(str(area or 'SinArea'))
    return base_dir / 'QRs' / 'Empleados' / area_safe


def generate_empleado_qr_image(empleado_obj):
    """
    Generate an employee QR card with:
      - Nombre
      - Apellidos
      - Area
      - ID de empleado
      - QR grande codificando el ID del empleado

    The image is saved under: BASE_DIR/QRs/Empleados/Area/empleado_<id>_<nombre>.png
    Returns the absolute path to the saved image.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import qrcode
    except Exception:
        return None

    empleado_id = getattr(empleado_obj, 'idempleado', '')
    nombre = str(getattr(empleado_obj, 'nombre', '') or '').strip()
    apellidos = str(getattr(empleado_obj, 'apellidos', '') or '').strip()
    area = str(getattr(empleado_obj, 'area', '') or '').strip()

    nombre_completo = f"{nombre} {apellidos}".strip() or 'SinNombre'
    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    out_dir = get_empleado_qr_folder(area)
    out_dir.mkdir(parents=True, exist_ok=True)

    width, height = _label_size_px()
    left_margin = 190
    qr_padding = 25

    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype('arialbd.ttf', 70)
        font_label = ImageFont.truetype('arial.ttf', 50)
        font_small = ImageFont.truetype('arial.ttf', 40)
    except Exception:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_small = ImageFont.load_default()

    qr_data = build_prefixed_qr_value('E', empleado_id)
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

    # Keep the QR large so it can be scanned from farther distance.
    target_qr_side = min(height - (qr_padding * 2), int(width * 0.42))
    if hasattr(Image, 'Resampling'):
        qr_img = qr_img.resize((target_qr_side, target_qr_side), Image.Resampling.NEAREST)
    else:
        qr_img = qr_img.resize((target_qr_side, target_qr_side), Image.NEAREST)

    qr_img = _overlay_logo_on_qr(qr_img, base_dir)

    qr_x = width - target_qr_side - qr_padding
    qr_y = (height - target_qr_side) // 2

    # Wrap text to available left area and center the block vertically.
    text_max_width = max(200, qr_x - (left_margin * 2))

    def _wrap_text_lines(text, font, max_width):
        words = str(text or '').split()
        if not words:
            return ['']

        lines = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            bbox = draw.textbbox((0, 0), candidate, font=font)
            candidate_width = bbox[2] - bbox[0]
            if candidate_width <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines

    def _line_height(font):
        bbox = draw.textbbox((0, 0), 'Ag', font=font)
        return bbox[3] - bbox[1]

    name_lines = _wrap_text_lines(nombre_completo, font_title, text_max_width)
    area_lines = _wrap_text_lines(f"Area: {area}", font_label, text_max_width)

    name_line_h = _line_height(font_title)
    area_line_h = _line_height(font_label)
    name_gap = 16
    area_gap = 14
    block_gap = 34

    name_height = (len(name_lines) * name_line_h) + (max(0, len(name_lines) - 1) * name_gap)
    area_height = (len(area_lines) * area_line_h) + (max(0, len(area_lines) - 1) * area_gap)
    total_text_height = name_height + block_gap + area_height

    start_y = max(44, (height - total_text_height) // 2)
    y = start_y

    for line in name_lines:
        draw.text((left_margin, y), line, font=font_title, fill=(0, 0, 0))
        y += name_line_h + name_gap

    y += block_gap - name_gap

    for line in area_lines:
        draw.text((left_margin, y), line, font=font_label, fill=(0, 0, 0))
        y += area_line_h + area_gap

    img.paste(qr_img, (qr_x, qr_y))

    filename = f"{_safe_name(nombre_completo)}_{empleado_id}.png"
    out_path = out_dir / filename
    img.save(out_path, format='PNG', dpi=(LABEL_DPI, LABEL_DPI))
    return str(out_path)


def get_pedido_qr_folder(order_number: str, folio: str, color: str):
    """
    Return absolute path for the QR folder of a specific pedido.
    Folder pattern: BASE_DIR/QRs/NumeroOrden/Folio-Color
    """
    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    order_safe = _safe_name(str(order_number))
    folio_color_safe = _safe_name(f"{folio}-{color}")
    return base_dir / 'QRs' / 'Ordenes' / order_safe / folio_color_safe

def decode_qr_from_image(image_file):
    """
    Decodifica un QR de una imagen (PIL Image o archivo).
    Retorna el contenido del QR o None si no puede decodificar.
    """
    try:
        # Intentamos con pyzbar primero
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            import io
            
            # Si es un archivo, lo convertimos a PIL Image
            if hasattr(image_file, 'read'):
                img = Image.open(image_file)
            else:
                img = image_file
                
            decoded_objects = decode(img)
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except ImportError:
            pass
        
        # Fallback: intentamos con OpenCV y pyzbar
        try:
            import cv2
            import numpy as np
            from pyzbar.pyzbar import decode
            from PIL import Image
            import io
            
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                nparr = np.frombuffer(image_data, np.uint8)
                img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img_cv = cv2.cvtColor(np.array(image_file), cv2.COLOR_RGB2BGR)
            
            img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
            decoded_objects = decode(img_pil)
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        except ImportError:
            pass
            
        # Fallback simple: usar CV2 para decodificar
        try:
            import cv2
            import numpy as np
            import io
            
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                image_file.seek(0)
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            else:
                img = cv2.cvtColor(np.array(image_file), cv2.COLOR_RGB2GRAY)
            
            detector = cv2.QRCodeDetector()
            data, pts, straight_qr = detector.detectAndDecode(img)
            if data:
                return data
        except ImportError:
            pass
            
    except Exception as e:
        print(f"Error decodificando QR: {e}")
    
    return None