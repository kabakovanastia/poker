import secrets
from ShamirCrypt import gen_prime, miller_rabin

class SchnorrSigner:
    def __init__(self):
        self.q = gen_prime(256)
        self.p = 2 * self.q + 1
        while not miller_rabin(self.p):
            self.q = gen_prime(256)
            self.p = 2 * self.q + 1
        
        h = 2
        while True:
            g = pow(h, (self.p - 1) // self.q, self.p)
            if g != 1:
                self.g = g
                break
            h += 1
        
        # Приватный ключ x
        self.x = secrets.randbelow(self.q - 1) + 1
        # Публичный ключ y
        self.y = pow(self.g, self.x, self.p)

    def sign(self, message):
        k = secrets.randbelow(self.q - 1) + 1
        # r = g^k mod p
        r = pow(self.g, k, self.p) % self.q
        # e = H(m, r) mod q (H - упрощённый хеш)
        e = self._hash(message, r) % self.q
        # s = (k + e * x) mod q
        s = (k + e * self.x) % self.q
        return (r, s)

    def verify(self, message, signature):
        r, s = signature
        if r <= 0 or r >= self.q or s <= 0 or s >= self.q:
            return False
        
        # e = H(m, r) mod q
        e = self._hash(message, r) % self.q
        # v1 = g^s mod p
        v1 = pow(self.g, s, self.p)
        # v2 = y^(-e) * r mod p
        y_inv_e = pow(self.y, -e, self.p)
        v2 = (y_inv_e * r) % self.p
        return (v1 % self.q) == r

    def _hash(self, message, r):
        # Простой "хеш" как сумма байтов данных
        # message - кортеж чисел (например, расшифрованная колода)
        # r - число
        total = r
        for m in message:
            total ^= m
            total = ((total << 1) | (total >> 63)) & 0xFFFFFFFFFFFFFFFF # Ротация
            total ^= m
        return total