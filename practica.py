import requests

def aplicar_xor_hex(hex_completo, valor_xor):
    """
    Aplica XOR a los últimos 2 caracteres de los primeros 32 caracteres del hexadecimal
    Args:
        hex_completo: Cadena hexadecimal completa (ej: 82a6f4f7...ded42f7)
        valor_xor: Valor hexadecimal (00-FF) para aplicar XOR
    Returns:
        Hex modificado con el XOR aplicado
    """
    if len(hex_completo) < 32:
        raise ValueError("El hexadecimal debe tener al menos 32 caracteres")
    
    # Separar las partes
    primeros_30 = hex_completo[:30]  # Primeros 30 caracteres
    ultimos_2 = hex_completo[30:32]   # Últimos 2 caracteres a modificar
    resto = hex_completo[32:]         # Resto del hexadecimal
    
    # Convertir a enteros
    original = int(ultimos_2, 16)
    xor = int(valor_xor, 16)
    
    # Aplicar XOR
    modificado = original ^ xor
    
    # Convertir de vuelta a hexadecimal (2 caracteres)
    nuevos_ultimos_2 = f"{modificado:02x}"
    
    # Reconstruir el hexadecimal completo
    return primeros_30 + nuevos_ultimos_2 + resto

def probar_combinaciones(hex_original):
    """Prueba todas las combinaciones XOR posibles"""
    base_url = "http://64.227.29.191/validador.cbc?ciphertext="
    exitos = []
    
    print(f"Hexadecimal original completo:\n{hex_original}")
    print(f"\nPrimeros 32 caracteres:\n{hex_original[:32]}")
    print(f"Últimos 2 caracteres a modificar: {hex_original[30:32]}")
    print("\nIniciando prueba de todas las combinaciones XOR (00 a FF)...")
    
    # Generar todos los valores hexadecimales posibles (00 a FF)
    for i in range(256):
        valor_xor = f"{i:02x}"  # Formato hexadecimal de 2 dígitos
        
        try:
            # Aplicar XOR y construir URL
            hex_modificado = aplicar_xor_hex(hex_original, valor_xor)
            url = base_url + hex_modificado
            
            # Hacer la petición
            respuesta = requests.get(url, timeout=5)
            resultado = respuesta.text.strip()
            
            # Mostrar progreso
            if i % 16 == 0:  # Mostrar cada 16 intentos
                print(f"Probando XOR {valor_xor}...")
            
            # Registrar exitos
            if resultado == "OK":
                print(f"\n¡ÉXITO con XOR {valor_xor}!")
                print(f"Hex modificado: {hex_modificado}")
                exitos.append((valor_xor, hex_modificado, url))
                
        except requests.RequestException as e:
            print(f"Error con XOR {valor_xor}: {str(e)}")
            continue
    
    # Mostrar resultados
    print("\n\nRESULTADOS FINALES:")
    if exitos:
        print(f"Se encontraron {len(exitos)} combinaciones válidas:")
        for i, (xor, hex_mod, url) in enumerate(exitos, 1):
            print(f"\nCombinación {i}:")
            print(f"Valor XOR: {xor}")
            print(f"Hex modificado: {hex_mod}")
            print(f"URL exitosa: {url}")
    else:
        print("No se encontraron combinaciones que devuelvan 'OK'")
    
    return exitos

# Ejecución principal
if __name__ == "__main__":
    hex_completo = "82a6f4f7a60f9798f167bf61232d7754824d8538ded42f7"
    
    if len(hex_completo) < 32:
        print("Error: El hexadecimal debe tener al menos 32 caracteres")
    else:
        resultados = probar_combinaciones(hex_completo)
        