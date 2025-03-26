import requests
from binascii import unhexlify, hexlify

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

class PaddingOracleAttack:
    def __init__(self, url):
        self.url = url
        self.block_size = 16  # AES block size is 16 bytes
    
    def make_request(self, ciphertext_hex):
        url = f"{self.url}{ciphertext_hex}"
        try:
            response = requests.get(url, timeout=3)
            return "OK" in response.text.upper()
        except:
            return False
    
    def decrypt_block(self, ciphertext, previous_block):
        decrypted = bytearray(self.block_size)
        
        for byte_pos in range(self.block_size-1, -1, -1):
            padding_value = self.block_size - byte_pos
            
            # Prepare modified previous block
            modified_prev = bytearray(previous_block)
            
            # Apply already known bytes
            for known_pos in range(byte_pos+1, self.block_size):
                modified_prev[known_pos] ^= decrypted[known_pos] ^ padding_value
            
            # Brute-force current byte
            found = False
            for guess in range(256):
                modified_prev[byte_pos] = previous_block[byte_pos] ^ guess ^ padding_value
                
                # Convert to hex and make request
                modified_ciphertext = hexlify(modified_prev + ciphertext).decode()
                if self.make_request(modified_ciphertext):
                    decrypted[byte_pos] = guess
                    found = True
                    print(f"Found byte {byte_pos}: {hex(guess)}")
                    break
            
            if not found:
                raise Exception(f"Failed to decrypt byte at position {byte_pos}")
        
        return bytes(decrypted)
    
    def decrypt(self, ciphertext_hex):
        ciphertext = unhexlify(ciphertext_hex)
        if len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext length must be multiple of block size")
        
        blocks = [ciphertext[i:i+self.block_size] 
                 for i in range(0, len(ciphertext), self.block_size)]
        
        plaintext = b""
        for i in range(len(blocks)-1, 0, -1):
            print(f"\nDecrypting block {i}...")
            decrypted = self.decrypt_block(blocks[i], blocks[i-1])
            plaintext = decrypted + plaintext
        
        # Remove padding
        padding_length = plaintext[-1]
        if padding_length <= self.block_size:
            plaintext = plaintext[:-padding_length]
        
        return plaintext

# Example usage
if __name__ == "__main__":
    url = "http://64.227.29.191/validador.cbc?ciphertext="
    ciphertext = "82a6f4f7a60f9798f167bf61232d7754824d8538ded42f7e4a53915327c07456"
    
    oracle = PaddingOracleAttack(url)
    print("Starting padding oracle attack...")
    
    try:
        plaintext = oracle.decrypt(ciphertext)
        print("\nDecrypted plaintext:", plaintext)
        print("As hex:", hexlify(plaintext).decode())
    except Exception as e:
        print("Attack failed:", str(e))