from pathlib import Path
from django.conf import settings
import os
import shutil

def _safe_name(s: str) -> str:
    # simple sanitizer for folder names
    return ''.join(c for c in s if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')

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
        order_dir = base_dir / 'QRs' / order_safe
        
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
    cantidad_str = str(pedido.cantidad)
    talla_str = str(pedido.talla)
    
    order_num = orden.numeroorden
    lote_id = lote_obj.idlote

    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    # build folder: QRs/NumeroOrden/Folio-Color
    order_safe = _safe_name(str(order_num))
    folio_color_safe = _safe_name(f"{folio_str}-{color_str}")
    out_dir = base_dir / 'QRs' / order_safe / folio_color_safe
    out_dir.mkdir(parents=True, exist_ok=True)

    # image layout - larger image to fit more information
    width = 900
    height = 400
    bg_color = (255, 255, 255)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # fonts (fallback to default)
    try:
        font_xlarge = ImageFont.truetype('arial.ttf', 40)  # For MODELO
        font_large = ImageFont.truetype('arial.ttf', 20)
        font_small = ImageFont.truetype('arial.ttf', 16)
    except Exception:
        font_xlarge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Layout: Left side with info, Right side with QR
    padding = 15
    x_text = padding
    y = padding
    
    # MODELO - Large at top
    draw.text((x_text, y), f"{model_str}", font=font_xlarge, fill=(0, 0, 0))
    y += 50
    
    # Folio and Cantidad
    draw.text((x_text, y), f"Folio: {folio_str:<15} Cant. chinelas: {cantidad_str}", font=font_small, fill=(0, 0, 0))
    y += 28
    
    # Talla, Maq tejido, Turno
    draw.text((x_text, y), f"Talla: {talla_str}", font=font_small, fill=(0, 0, 0))
    y += 28
    
    # Color, Operador
    draw.text((x_text, y), f"Color: {color_str:<25}", font=font_small, fill=(0, 0, 0))
    y += 28
    
    # Lote info
    draw.text((x_text, y), f"Lote: {lote_number}/{total_lotes}", font=font_large, fill=(0, 0, 0))

    # generate QR for lote_id
    qr_data = str(lote_id)
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

    # Make QR occupy almost half of the image/card visual space
    target_qr_side = min(height - (padding * 2), int(width * 0.48))
    if hasattr(Image, 'Resampling'):
        qr_img = qr_img.resize((target_qr_side, target_qr_side), Image.Resampling.NEAREST)
    else:
        qr_img = qr_img.resize((target_qr_side, target_qr_side), Image.NEAREST)

    # paste QR on right side
    qr_w, qr_h = qr_img.size
    qr_x = width - qr_w - padding
    qr_y = (height - qr_h) // 2
    img.paste(qr_img, (qr_x, qr_y))

    # save file
    filename = f"lote_{lote_number}.png"
    out_path = out_dir / filename
    img.save(out_path, format='PNG')
    return str(out_path)


def get_pedido_qr_folder(order_number: str, folio: str, color: str):
    """
    Return absolute path for the QR folder of a specific pedido.
    Folder pattern: BASE_DIR/QRs/NumeroOrden/Folio-Color
    """
    base_dir = Path(getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent))
    order_safe = _safe_name(str(order_number))
    folio_color_safe = _safe_name(f"{folio}-{color}")
    return base_dir / 'QRs' / order_safe / folio_color_safe
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