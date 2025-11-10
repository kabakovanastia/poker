import random
import secrets
import math

KEY_SIZE = 2048

def check_small_prime(n):
    for p in PRIME_NUMS:
        if n % p == 0:
            if n == p:
                continue
            return False
    return True

def miller_rabin(n, k=30):
    # x - 1 = 2^s * d
    d = n - 1
    s = 0
    while d & 1 == 0:
        s += 1
        d >>= 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if (x == 1) or (x == n - 1):
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gen_prime(n):
    rand_odd = secrets.randbits(n) | ((1 << (n - 1)) + 1)
    g = 0
    while not (miller_rabin(rand_odd, k=30)):
        g += 1
        rand_odd += 2
        if rand_odd.bit_length() > n:
            rand_odd = secrets.randbits(n) | ((1 << (n - 1)) + 1)

    return rand_odd

def get_rsa_keys(n, e):
    p = gen_prime(n // 2 - 2)
    q = gen_prime(n // 2 + 2)

    while True:
        if (p - 1) % e == 0:
            p = gen_prime(n // 2 - 2)
            continue
        if (q - 1) % e == 0:
            q = gen_prime(n // 2 + 2)
            continue
        break

    N = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)

    return (e, N), (d, N)

def rsa_encrypt(message, key):
    return pow(message, key[0], key[1])

def rsa_decrypt(message, key):
    return pow(message, key[0], key[1])


def gen_shamir_key(prime):
    rand_odd = secrets.randbelow(prime - 2) | 1

    while True:
        if math.gcd(rand_odd, prime - 1) == 1:
            break

        if rand_odd >= prime - 1:
            rand_odd = secrets.randbelow(prime - 2) | 1

        rand_odd += 2

    return (rand_odd, pow(rand_odd, -1, prime - 1), prime)

def shamir_encrypt(message, key):
    return [pow(m, key[0], key[2]) for m in message]

def shamir_decrypt(message, key):
    return [pow(m, key[1], key[2]) for m in message]

class ShamirCrypt():
    def __init__(self, prime):
        self.prime = prime
        self.key = gen_shamir_key(prime)

    def encrypt(self, msg):
        return shamir_encrypt(msg, self.key)

    def decrypt(self, msg):
        return shamir_decrypt(msg, self.key)
