from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import hashlib
import base64

def aesEncrypt(message, key):
    hash_key = hashlib.md5(key.encode('utf-8')).digest()
    cipher = AES.new(hash_key, AES.MODE_CBC, hash_key)
    padded_message = pad(message.encode(), AES.block_size, style='pkcs7')
    ciphertext = cipher.encrypt(padded_message)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext.decode('utf-8')

def aesDecrypt(text, key):
    ciphertext = text.encode()
    hash_key = hashlib.md5(key.encode('utf-8')).digest()
    cipher = AES.new(hash_key, AES.MODE_CBC, hash_key)
    ciphertext = base64.b64decode(ciphertext)
    plaintext = cipher.decrypt(ciphertext)
    plaintext = unpad(plaintext, AES.block_size, style='pkcs7')
    return plaintext.decode('utf-8')

def genKey(message):
    md5_hash = hashlib.md5(message.encode('utf-8')).hexdigest()
    return md5_hash

def genToken(data):
    sha384_hash = hashlib.sha384(data.encode()).digest()
    return sha384_hash.hex()

# if __name__ == '__main__':
#     # message = ""
#     # key = ""
#     # encrypted_message = aesEncrypt(message, key)
#     # print("生成的密文:", encrypted_message)
#     # decrypted_message = aesDecrypt("", "")
#     # print("解密后的明文:", decrypted_message)
#     # # print("生成的密钥:", key)