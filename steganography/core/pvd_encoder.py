import numpy as np
from core.pvd_utils import load_image_as_matrix, get_blocks, difference, quantization
import math
from PIL import Image
from cryptography.fernet import Fernet

def text_to_bits(text, key):
    """
    Metni okur, başına TXT| etiketi ve sonuna [EOF] ekleyerek bit dizisine dönüştürür.
    (Decoder'ın bunun bir metin olduğunu anlaması için TXT| başlığı eklendi)
    """
    f = Fernet(key)
    encrypted_data = f.encrypt(text.encode('utf-8'))

    payload = b"TXT|" + encrypted_data + b"[EOF]"
    bits = bin(int.from_bytes(payload, 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def image_to_bits(secret_image_path, key):
    """
    Gizli görseli okur, başına IMG| etiketi ve sonuna [EOF] ekleyerek 
    bit (0 ve 1) dizisine dönüştürür.
    """
    try:
        f = Fernet(key)
        with open(secret_image_path, "rb") as file:
            image_bytes = file.read()

        encrypted_data = f.encrypt(image_bytes)
        full_payload = b"IMG|" + encrypted_data + b"[EOF]"

        bits = bin(int.from_bytes(full_payload, 'big'))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    except FileNotFoundError:
        raise ValueError("Gizlenecek görsel dosyası bulunamadı.")
    except Exception as e:
        raise ValueError(f"Görsel şifrelenirken bir hata oluştu: {e}")

def update_pixels(p1, p2, d_prime, d):
    d2 = d_prime - d

    p1_new = p1 + math.ceil(d2 / 2)
    p2_new = p2 - math.floor(d2 / 2)

    # ÇÖZÜM: Farkı (d_prime) koruyarak sınır aşımını düzelt
    if p1_new > 255:
        shift = p1_new - 255
        p1_new -= shift
        p2_new -= shift
    elif p1_new < 0:
        shift = 0 - p1_new
        p1_new += shift
        p2_new += shift

    if p2_new > 255:
        shift = p2_new - 255
        p1_new -= shift
        p2_new -= shift
    elif p2_new < 0:
        shift = 0 - p2_new
        p1_new += shift
        p2_new += shift

    p1_new = max(0, min(255, p1_new))
    p2_new = max(0, min(255, p2_new))

    return p1_new, p2_new


def encode(matrix, binary_message):
    max_capacity = matrix.size * 3  # teorik üst sınır
    if len(binary_message) > max_capacity:
        raise ValueError("Gizlenecek veri çok büyük!")

    message_index = 0
    stego_matrix = matrix.copy()

    for coords, p1, p2 in get_blocks(stego_matrix):
        # Mesajın tamamı yazıldıysa döngüyü bitir
        if message_index >= len(binary_message):
            break

        difference_params = difference(p1, p2)
        d = difference_params[0]
        abs_diff = difference_params[1]

        res = quantization(abs_diff)
        if res is None:
            continue

        low, high, bit_count = res
        bit_count = int(bit_count)

        current_bits = binary_message[message_index: message_index + bit_count]
        if not current_bits:
            break
        if len(current_bits) < bit_count:
            current_bits = current_bits.ljust(bit_count, '0')

        actual_n = len(current_bits)
        S = int(current_bits, 2)

        new_abs = low + S
        if d >= 0:
            d_prime = new_abs
        else:
            d_prime = -new_abs

        stego_p1, stego_p2 = update_pixels(p1, p2, d_prime, d)

        y, x, c = coords
        stego_matrix[y, x, c] = stego_p1
        stego_matrix[y, x + 1, c] = stego_p2

        message_index += actual_n

    # YENİ EKLENEN KONTROL: Eğer pikseller bitti ama mesaj bitmediyse uyar!
    if message_index < len(binary_message):
        raise ValueError(
            "Kapak görselinin pikselleri yetersiz kaldı! Şifreleme (AES) verinin boyutunu büyüttüğü için lütfen daha yüksek çözünürlüklü (örn. 1920x1080) bir kapak görseli veya daha küçük boyutlu bir gizli görsel seçin.")

    stego_image = Image.fromarray(stego_matrix.astype(np.uint8))
    return stego_image