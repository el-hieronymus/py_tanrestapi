from cryptography.fernet import Fernet
import json

# encapulate the encryption and decryption in a class
class TanRESTcypher:

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
        with open(json_file, 'r') as infile:
            data = json.load(infile)
        encrypted_api_key = data['api_key']
        return encrypted_api_key

    def write_key_json(self, json_file, encrypted_api_key):
        # Write the encrypted information to the JSON file
        with open(json_file, 'w') as outfile:
            json.dump({'api_key': encrypted_api_key}, outfile)
            
    def print_key_json(self, json_file):
        # Read the encrypted information from the JSON file
        with open(json_file, 'r') as infile:
            data = json.load(infile)
        encrypted_api_key = data['api_key']
        print(encrypted_api_key)
# End class TanRESTcypher