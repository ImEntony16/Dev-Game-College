# -*- coding: cp1251 -*-
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# ==========================================
# Завдання 1: Симетричне шифрування
# ==========================================
def task1_symmetric():
    print("=== Завдання 1: Симетричне шифрування ===")
    
    # 1. Генерація ключа шифрування
    correct_key = Fernet.generate_key()
    cipher = Fernet(correct_key)
    print(f"Згенерований ключ: {correct_key.decode()}")

    # 2. Шифрування текстового повідомлення
    original_message = "Це дуже секретне повідомлення!".encode('utf-8')
    encrypted_message = cipher.encrypt(original_message)
    print(f"Зашифроване повідомлення: {encrypted_message}")

    # 3. Розшифрування повідомлення
    decrypted_message = cipher.decrypt(encrypted_message)
    print(f"Розшифроване повідомлення: {decrypted_message.decode('utf-8')}")

    # 4. Спроба розшифрування з неправильним ключем
    wrong_key = Fernet.generate_key()
    wrong_cipher = Fernet(wrong_key)
    
    try:
        print("\nСпроба розшифрувати неправильним ключем...")
        wrong_cipher.decrypt(encrypted_message)
    except InvalidToken:
        print("Помилка: Невірний ключ! Розшифрування неможливе (як і очікувалося).")
    print("\n")


# ==========================================
# Завдання 2: Асиметричне шифрування
# ==========================================
def task2_asymmetric():
    print("=== Завдання 2: Асиметричне шифрування ===")
    
    # 1. Генерація пари ключів (публічного та приватного)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    print("Пару ключів (RSA 2048) успішно згенеровано.")

    # 2. Шифрування повідомлення публічним ключем
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

    # 3. Розшифрування приватним ключем
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"Розшифроване повідомлення (приватним ключем): {plaintext.decode('utf-8')}\n")


# ==========================================
# Завдання 3: Асиметричне шифрування + Симетричне
# ==========================================
class Network:
    """Простий клас для симуляції перехоплення/передачі даних по мережі"""
    @staticmethod
    def transmit(sender_name, receiver_name, data_description, data):
        print(f"[Мережа] {sender_name} відправляє '{data_description}' -> {receiver_name}")
        return data

class UserA:
    def __init__(self):
        self.name = "Користувач А"
        # Генерація пари ключів при створенні користувача
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.symmetric_cipher = None

    def get_public_key(self):
        return self.public_key

    def receive_symmetric_key(self, encrypted_symmetric_key):
        # Розшифрування симетричного ключа своїм приватним ключем
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
        # Створення симетричного ключа
        self.symmetric_key = Fernet.generate_key()
        self.symmetric_cipher = Fernet(self.symmetric_key)
        self.foreign_public_key = None

    def receive_public_key(self, public_key):
        self.foreign_public_key = public_key
        print(f"[{self.name}] Отримав публічний ключ від Користувача А.")

    def get_encrypted_symmetric_key(self):
        # Шифрування свого симетричного ключа чужим публічним ключем
        encrypted_key = self.foreign_public_key.encrypt(
            self.symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key

    def encrypt_message(self, text):
        return self.symmetric_cipher.encrypt(text.encode('utf-8'))

    def decrypt_message(self, encrypted_text):
        return self.symmetric_cipher.decrypt(encrypted_text).decode('utf-8')

def task3_hybrid():
    print("=== Завдання 3: Асиметричне + Симетричне шифрування (Гібридне) ===")
    
    alice = UserA()
    bob = UserB()

    # 1. Відправка публічного ключа користувачу Б
    pub_key = Network.transmit(alice.name, bob.name, "Публічний RSA ключ", alice.get_public_key())
    bob.receive_public_key(pub_key)

    # 2. Шифрування та відправка симетричного ключа початковому користувачу
    enc_sym_key = bob.get_encrypted_symmetric_key()
    received_enc_key = Network.transmit(bob.name, alice.name, "Зашифрований симетричний ключ", enc_sym_key)
    
    # 3. Розшифрування симетричного ключа
    alice.receive_symmetric_key(received_enc_key)

    print("\n--- Початок безпечного чату (на базі симетричного ключа) ---")
    
    # 4. Обмін повідомленнями
    msg_from_a = "Привіт, Б! Як чути?"
    enc_msg_a = alice.encrypt_message(msg_from_a)
    delivered_msg_a = Network.transmit(alice.name, bob.name, "Зашифроване повідомлення від А", enc_msg_a)
    print(f"[{bob.name}] Розшифрував: {bob.decrypt_message(delivered_msg_a)}\n")

    msg_from_b = "Чути чудово, А! Ключі працюють."
    enc_msg_b = bob.encrypt_message(msg_from_b)
    delivered_msg_b = Network.transmit(bob.name, alice.name, "Зашифроване повідомлення від Б", enc_msg_b)
    print(f"[{alice.name}] Розшифрував: {alice.decrypt_message(delivered_msg_b)}")


# ==========================================
# Запуск усіх завдань
# ==========================================
if __name__ == "__main__":
    task1_symmetric()
    task2_asymmetric()
    task3_hybrid()
