# -*- coding: cp1251 -*-
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Завдання 1
def task1_symmetric():
    print("=== Завдання 1: Симетричне шифрування ===")
    
    # Генерую ключ
    correct_key = Fernet.generate_key()
    cipher = Fernet(correct_key)
    print(f"Згенерований ключ: {correct_key.decode()}")

    # Шифрую текст
    original_message = "Це дуже секретне повідомлення!".encode('utf-8')
    encrypted_message = cipher.encrypt(original_message)
    print(f"Зашифроване повідомлення: {encrypted_message}")

    # Дешифрую текст
    decrypted_message = cipher.decrypt(encrypted_message)
    print(f"Розшифроване повідомлення: {decrypted_message.decode('utf-8')}")

    # Лівий ключ
    wrong_key = Fernet.generate_key()
    wrong_cipher = Fernet(wrong_key)
    
    try:
        print("\nСпроба розшифрувати неправильним ключем...")
        wrong_cipher.decrypt(encrypted_message)
    except InvalidToken:
        print("Помилка: Невірний ключ! Розшифрування неможливе (як і очікувалося).")
    print("\n")


# Завдання 2
def task2_asymmetric():
    print("=== Завдання 2: Асиметричне шифрування ===")
    
    # Пара ключів
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    print("Пару ключів (RSA 2048) успішно згенеровано.")

    # Шифрую публічним
    message = "Асиметрична таємниця".encode('utf-8')
    
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"Зашифроване повідомлення (публічним ключем): {ciphertext.hex()[:50]}...")

    # Дешифрую приватним
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"Розшифроване повідомлення (приватним ключем): {plaintext.decode('utf-8')}\n")


# Завдання 3
class Network:
    # Симуляція мережі
    @staticmethod
    def transmit(sender_name, receiver_name, data_description, data):
        print(f"[Мережа] {sender_name} відправляє '{data_description}' -> {receiver_name}")
        return data

class UserA:
    def __init__(self):
        self.name = "Користувач А"
        # Мої ключі
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.symmetric_cipher = None

    def get_public_key(self):
        return self.public_key

    def receive_symmetric_key(self, encrypted_symmetric_key):
        # Дешифрую ключ
        symmetric_key = self.private_key.decrypt(
            encrypted_symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.symmetric_cipher = Fernet(symmetric_key)
        print(f"[{self.name}] Успішно розшифрував симетричний ключ!")

    def encrypt_message(self, text):
        return self.symmetric_cipher.encrypt(text.encode('utf-8'))

    def decrypt_message(self, encrypted_text):
        return self.symmetric_cipher.decrypt(encrypted_text).decode('utf-8')

class UserB:
    def __init__(self):
        self.name = "Користувач Б"
        # Мій симетричний
        self.symmetric_key = Fernet.generate_key()
        self.symmetric_cipher = Fernet(self
