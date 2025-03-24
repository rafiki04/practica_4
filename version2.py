import requests
from time import sleep

def modificar_byte(hex_str, pos, xor_val):
    """Modifica un byte específico en una cadena hexadecimal"""
    if pos % 2 != 0 or pos < 0 or pos >= len(hex_str):
        raise ValueError("Posición debe ser par y dentro de la cadena")
    
    byte_actual = int(hex_str[pos:pos+2], 16)
    byte_modificado = byte_actual ^ xor_val
    return hex_str[:pos] + f"{byte_modificado:02x}" + hex_str[pos+2:]

def probar_byte(url_base, hex_completo, pos, delay=0.1):
    """Prueba todos los valores XOR para un byte específico"""
    print(f"\nAtacando posición {pos}-{pos+1} (valor actual: {hex_completo[pos:pos+2]})")
    
    for xor_val in range(256):
        modificado = modificar_byte(hex_completo, pos, xor_val)
        url = url_base + modificado
        
        try:
            sleep(delay)  # Evitar saturación del servidor
            respuesta = requests.get(url, timeout=5)
            
            if respuesta.status_code == 200:
                resultado = respuesta.text.strip()
                
                if resultado == "OK":
                    print(f"¡ÉXITO! Posición {pos}: XOR {xor_val:02x}")
                    print(f"Hex modificado: {modificado}")
                    print(f"URL válida: {url}")
                    return modificado, xor_val
                
        except Exception as e:
            print(f"Error en XOR {xor_val:02x}: {str(e)}")
            continue
    
    print("No se encontró un XOR válido para esta posición")
    return None, None

def ataque_cbc(hex_completo):
    """Realiza el ataque CBC byte a byte"""
    url_base = "http://64.227.29.191/validador.cbc?ciphertext="
    bloque = hex_completo[:32]
    resultado = bloque
    xor_values = []
    
    # Atacamos desde el final hacia el inicio (posiciones 30,28,...,0)
    for pos in range(30, -1, -2):
        resultado, xor_val = probar_byte(url_base, resultado, pos)
        
        if not resultado:
            print("\n¡Ataque fallido! No se puede continuar.")
            return None
        
        xor_values.append((pos, xor_val))
        print(f"\nProgreso: {int((30-pos)/2)+1}/16 bytes modificados")
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Hex original: {hex_completo}")
    print(f"Hex modificado: {resultado + hex_completo[32:]}")
    
    print("\nValores XOR utilizados (orden inverso):")
    for pos, xor_val in xor_values:
        print(f"Byte {pos//2}: XOR {xor_val:02x} en pos {pos}-{pos+1}")
    
    return resultado + hex_completo[32:]

if __name__ == "__main__":
    # Tu hexadecimal completo
    hex_original = "82a6f4f7a60f9798f167bf61232d7754824d8538ded42f7"
    
    print("Iniciando ataque CBC byte a byte...")
    print(f"Longitud del hexadecimal: {len(hex_original)} caracteres")
    
    if len(hex_original) < 32:
        print("Error: Se necesitan al menos 32 caracteres hexadecimales")
    else:
        resultado_final = ataque_cbc(hex_original)
        
        if resultado_final:
            print("\nAtaque completado con éxito!")
            print("Hex completo válido:", resultado_final)