from cryptography.fernet import Fernet
import json
import argparse

# encapsulate the encryption and decryption in a class
class TanCipher:

    def __init__(self, key=None):
        if key is None:
            self._key = Fernet.generate_key()
        else:
            self._key = key

    # Encrypt the data
    def encrypt(self, data):
        cipher_suite = Fernet(self._key)
        encrypted_text = cipher_suite.encrypt(data.encode('utf-8'))
        return encrypted_text.decode('utf-8')

    # Decrypt the data
    def decrypt(self, data):
        cipher_suite = Fernet(self._key)
        decrypted_text = cipher_suite.decrypt(data.encode('utf-8'))
        return decrypted_text.decode('utf-8')

    # Generate a key for encryption and decryption
    def generate_key(self):
        return Fernet.generate_key()

    def read_key_json(self, json_file):
        # Read the encrypted information from the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)
        encrypted_api_key = data['api_key']
        return encrypted_api_key

    def write_key_json(self, json_file, encrypted_api_key):
        # Write the encrypted information to the JSON file
        with open(json_file, 'w') as outfile:
            json.dump({'api_key': encrypted_api_key}, outfile)
            
    def print_key_json(self, json_file):
        # Read the encrypted information from the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)
        encrypted_api_key = data['api_key']
        print(encrypted_api_key)
# End class TanCipher

if __name__ == "__main__":
    tan_cipher = TanCipher()

    parser = argparse.ArgumentParser(description='Encrypt and decrypt API key')
    parser.add_argument('-e', '--encrypt', help='Encrypt the API key', action='store_true')
    parser.add_argument('-d', '--decrypt', help='Decrypt the API key', action='store_true')
    parser.add_argument('-g', '--generate', help='Generate a key for encryption and decryption', action='store_true')
    parser.add_argument('-r', '--read', help='Read the encrypted API key from the JSON file', action='store_true')
    parser.add_argument('-w', '--write', help='Write the encrypted API key to the JSON file', action='store_true')
    parser.add_argument('-p', '--print', help='Print the encrypted API key from the JSON file', action='store_true')
    args = parser.parse_args()

    if args.generate:
        # Generate a key for encryption and decryption
        key = tan_cipher.generate_key()
        print(key)
    elif args.read:
        # Read the encrypted information from the JSON file
        encrypted_api_key = tan_cipher.read_key_json(args.read)
        print(encrypted_api_key)
    elif args.write:
        # Write the encrypted information to the JSON file
        tan_cipher.write_key_json('tanRESTcipher.json', args.write)
    elif args.print:
        # Print the encrypted information from the JSON file
        tan_cipher.print_key_json(args.print)
    elif args.decrypt:
        # Decrypt the API key
        decrypted_api_key = tan_cipher.decrypt(args.decrypt)
        print(decrypted_api_key)
    elif args.encrypt:
        print("Encrypting API key: {}".format(args.encrypt))
        # # Encrypt the API key
        # encrypted_api_key = tan_cipher.encrypt(args.encrypt)
        # print("Re-encrypted API key: {}".format(encrypted_api_key))
    else:
        print("No action specified")

    encrypted_api_key = args.encrypt

    # Decrypt the API key
    decrypted_api_key = tan_cipher.decrypt(encrypted_api_key)
    print(decrypted_api_key)

    # Encrypt the API key
    encrypted_api_key = tan_cipher.encrypt(decrypted_api_key)
    print("Re-encrypted API key: {}".format(encrypted_api_key))

    # Write the encrypted information to the JSON file
    tan_cipher.write_key_json('tanRESTcipher.json', encrypted_api_key)
    tan_cipher.print_key_json('tanRESTcipher.json')
    