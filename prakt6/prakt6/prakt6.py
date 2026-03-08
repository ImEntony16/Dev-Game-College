import os
import hashlib
from abc import ABC, abstractmethod
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. Хешування (Перевірка цілісності)

class Hasher:
    """Клас для створення хешів (SHA-256)"""
    @staticmethod
    def generate_hash(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

# 2. Патерн "Стратегія"

class IEncryptionStrategy(ABC):
    """Інтерфейс для стратегій шифрування"""
    @abstractmethod
    def encrypt(self, data: bytes, key) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes, key) -> bytes:
        pass

class AESEncryptionStrategy(IEncryptionStrategy):
    """Симетричне шифрування (AES-GCM) для повідомлень"""
    def encrypt(self, data: bytes, key: bytes) -> bytes:
        aesgcm = AESGCM(key)
        nonce = os.urandom(12) # Унікальний вектор ініціалізації
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext # Зберігаємо nonce разом із шифротекстом

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        aesgcm = AESGCM(key)
        nonce = data[:12]
        ciphertext = data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)

class RSAEncryptionStrategy(IEncryptionStrategy):
    """Асиметричне шифрування (RSA) для обміну ключами"""
    def encrypt(self, data: bytes, public_key) -> bytes:
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt(self, data: bytes, private_key) -> bytes:
        return private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

# 3. Основні сутності (Entities)
class User:
    """Користувач системи з власною парою ключів RSA"""
    def __init__(self, name: str):
        self.name = name
        # Генерація приватного та публічного ключів
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()

    def get_public_key(self):
        return self.public_key

class Message:
    """Клас, що представляє захищене повідомлення"""
    def __init__(self, sender: User, receiver: User, encrypted_content: bytes, msg_hash: str, encrypted_aes_key: bytes):
        self.sender = sender
        self.receiver = receiver
        self.encrypted_content = encrypted_content
        self.msg_hash = msg_hash
        self.encrypted_aes_key = encrypted_aes_key


# 4. Сервіс обміну повідомленнями

class MessageService:
    """Сервіс для шифрування, передачі та перевірки повідомлень"""
    def __init__(self):
        self.rsa_strategy = RSAEncryptionStrategy()
        self.aes_strategy = AESEncryptionStrategy()

    def send_message(self, sender: User, receiver: User, plaintext: str):
        print(f"\n[{sender.name} -> {receiver.name}] Початок відправки...")

        # 1. Генерація AES ключа (Симетричний ключ)
        aes_key = AESGCM.generate_key(bit_length=256)
        print(" [+] Згенеровано одноразовий AES ключ.")

        # 2. Хешування (SHA-256)
        msg_hash = Hasher.generate_hash(plaintext)
        print(f" [+] Хеш повідомлення: {msg_hash}")

        # 3. Шифрування повідомлення (AES)
        encrypted_content = self.aes_strategy.encrypt(plaintext.encode('utf-8'), aes_key)
        print(" [+] Повідомлення зашифровано через AES.")

        # 4. Шифрування AES ключа (RSA публічним ключем отримувача)
        encrypted_aes_key = self.rsa_strategy.encrypt(aes_key, receiver.get_public_key())
        print(" [+] AES ключ зашифровано через RSA (Публічний ключ отримувача).")

        # Формування об'єкта повідомлення
        message = Message(sender, receiver, encrypted_content, msg_hash, encrypted_aes_key)
        
        # Симуляція передачі через мережу
        self._receive_message(receiver, message)

    def _receive_message(self, receiver: User, message: Message):
        print(f"\n[{receiver.name}] Отримання та обробка повідомлення...")

        try:
            # 1. Розшифрування AES ключа (RSA приватним ключем отримувача)
            aes_key = self.rsa_strategy.decrypt(message.encrypted_aes_key, receiver.private_key)
            print(" [+] AES ключ успішно розшифровано (Приватний ключ отримувача).")

            # 2. Розшифрування повідомлення (AES)
            decrypted_bytes = self.aes_strategy.decrypt(message.encrypted_content, aes_key)
            decrypted_text = decrypted_bytes.decode('utf-8')
            print(" [+] Повідомлення розшифровано через AES.")

            # 3. Перевірка цілісності (Хешування)
            calculated_hash = Hasher.generate_hash(decrypted_text)
            
            if calculated_hash == message.msg_hash:
                print(" [+] Перевірка цілісності: УСПІШНО! (Хеші збігаються)")
                print(f"\n---> Прочитане повідомлення: '{decrypted_text}'")
            else:
                print(" [-] Перевірка цілісності: ПОМИЛКА! (Повідомлення було змінено)")
                
        except Exception as e:
            print(f" [-] Помилка при розшифруванні: {e}")

# 5. Демонстрація роботи (Пайплайн)

if __name__ == "__main__":
    print("=== Симуляція захищеного обміну повідомленнями ===")
    
    # 1. Ініціалізація користувачів
    alice = User("Alice")
    bob = User("Bob")
    
    # 2. Ініціалізація сервісу
    service = MessageService()
    
    # 3. Передача повідомлення від Alice до Bob
    secret_message = "Привіт, Антон! Це надсекретні дані для проекту."
    service.send_message(sender=alice, receiver=bob, plaintext=secret_message)