import numpy as np
from core.pvd_utils import get_blocks, difference, quantization
from cryptography.fernet import Fernet

def decode(stego_matrix, key):
    byte_array = bytearray()
    bit_buffer = ""
    f = Fernet(key)
    
    # Tüm resmi değil, sadece veriyi bulana kadar tarayacağız
    for coords, p1, p2 in get_blocks(stego_matrix):
        difference_params = difference(p1, p2)
        abs_diff = difference_params[1]
        
        res = quantization(abs_diff)
        if res is None:
            continue
            
        low, high, bit_count = res
        S = max(0, min((high - low), abs_diff - low))
        
        # Gelen sayıyı bitlere çevir ve depoya (buffer) at
        bit_buffer += bin(S)[2:].zfill(int(bit_count))
        
        # Eğer depoda 8 bit (1 byte) veya daha fazlası biriktiyse...
        while len(bit_buffer) >= 8:
            # İlk 8 biti kopar, sayıya çevir ve diziye ekle
            byte_str = bit_buffer[:8]
            byte_array.append(int(byte_str, 2))
            bit_buffer = bit_buffer[8:] # Okunan kısmı sil
            
            # AKILLI ERKEN ÇIKIŞ (EARLY EXIT)
            if len(byte_array) > 4:
                header = byte_array[:4].decode('utf-8', errors='ignore')

                # Şifreli Metin Çıkarma
                if header == "TXT|":
                    if len(byte_array) >= 9 and byte_array[-5:] == b"[EOF]":
                        encrypted_payload = bytes(byte_array[4:-5])
                        try:
                            decrypted_bytes = f.decrypt(encrypted_payload)
                            text = decrypted_bytes.decode('utf-8')
                            return {"type": "text", "data": text}
                        except Exception as e:
                            return {"type": "error", "data": "Şifre çözülemedi. Yanlış anahtar!"}

                # Şifreli Görsel Çıkarma
                elif header == "IMG|":
                    if len(byte_array) >= 9 and byte_array[-5:] == b"[EOF]":
                        encrypted_payload = bytes(byte_array[4:-5])
                        try:
                            decrypted_bytes = f.decrypt(encrypted_payload)
                            return {"type": "image", "data": decrypted_bytes}
                        except Exception as e:
                            return {"type": "error", "data": "Şifre çözülemedi. Yanlış anahtar!"}

    # Eğer resmin en sonuna kadar gelir ve hiçbir şey bulamazsa:
    print("Uyarı: Görüntü sonuna gelindi ancak gizli veri etiketi [EOF] bulunamadı.")
    return {"type": "unknown", "data": byte_array}