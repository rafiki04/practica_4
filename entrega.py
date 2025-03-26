import requests
from binascii import unhexlify, hexlify

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

class AtaqueOraclePadding:
    def __init__(self, url):
        self.url = url
        self.tamano_bloque = 16
    
    def hacer_peticion(self, ciphertext_hex):
        url = f"{self.url}{ciphertext_hex}"
        try:
            respuesta = requests.get(url, timeout=3)
            return "OK" in respuesta.text.upper()
        except:
            return False
    
    def descifrar_bloque(self, ciphertext, bloque_anterior):
        descifrado = bytearray(self.tamano_bloque)
        
        for pos_byte in range(self.tamano_bloque-1, -1, -1):
            valor_padding = self.tamano_bloque - pos_byte
            bloque_anterior_modificado = bytearray(bloque_anterior)
            
            for pos_known in range(pos_byte+1, self.tamano_bloque):
                bloque_anterior_modificado[pos_known] ^= descifrado[pos_known] ^ valor_padding
            
            encontrado = False
            for adivinanza in range(256):
                bloque_anterior_modificado[pos_byte] = bloque_anterior[pos_byte] ^ adivinanza ^ valor_padding
                ciphertext_modificado = hexlify(bloque_anterior_modificado + ciphertext).decode()
                if self.hacer_peticion(ciphertext_modificado):
                    descifrado[pos_byte] = adivinanza
                    encontrado = True
                    print(f"Byte {pos_byte} encontrado: {hex(adivinanza)}")
                    break
            
            if not encontrado:
                raise Exception(f"No se pudo descifrar el byte {pos_byte}")
        
        return bytes(descifrado)
    
    def descifrar(self, ciphertext_hex):
        ciphertext = unhexlify(ciphertext_hex)
        if len(ciphertext) % self.tamano_bloque != 0:
            raise ValueError("Ciphertext inválido")
        
        bloques = [ciphertext[i:i+self.tamano_bloque] 
                  for i in range(0, len(ciphertext), self.tamano_bloque)]
        
        texto_plano = b""
        for i in range(len(bloques)-1, 0, -1):
            print(f"\nDescifrando bloque {i}...")
            descifrado = self.descifrar_bloque(bloques[i], bloques[i-1])
            texto_plano = descifrado + texto_plano
        
        tamano_padding = texto_plano[-1]
        if tamano_padding <= self.tamano_bloque:
            texto_plano = texto_plano[:-tamano_padding]
        
        return texto_plano

if __name__ == "__main__":
    url = "http://64.227.29.191/validador.cbc?ciphertext="
    ciphertext = "82a6f4f7a60f9798f167bf61232d7754824d8538ded42f7e4a53915327c07456"
    
    oracle = AtaqueOraclePadding(url)
    print("Iniciando ataque...")
    
    try:
        texto_plano = oracle.descifrar(ciphertext)
        print("\nTexto descifrado:", texto_plano)
        print("Hex:", hexlify(texto_plano).decode())
    except Exception as e:
        print("Error:", str(e))