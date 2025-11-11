import secrets
import math

def miller_rabin(n, k=30):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gen_prime(n):
    while True:
        candidate = secrets.randbits(n) | 1
        if miller_rabin(candidate):
            return candidate

def gen_shamir_key(prime):
    while True:
        e = secrets.randbelow(prime - 2) | 1
        if math.gcd(e, prime - 1) == 1:
            d = pow(e, -1, prime - 1)
            return (e, d, prime)

def shamir_encrypt(message, key):
    return [pow(m, key[0], key[2]) for m in message]

def shamir_decrypt(message, key):
    return [pow(m, key[1], key[2]) for m in message]

class ShamirCrypt:
    def __init__(self, prime):
        self.prime = prime
        self.key = gen_shamir_key(prime)

    def encrypt(self, msg):
        return shamir_encrypt(msg, self.key)

    def decrypt(self, msg):
        return shamir_decrypt(msg, self.key)