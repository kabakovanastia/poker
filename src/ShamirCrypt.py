import random
import secrets
import math

KEY_SIZE = 2048
PRIME_NUMS = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 
    509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 
    613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 
    821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 
    919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
]

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
        if x in [1, n - 1]:
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

    while math.gcd(rand_odd, prime - 1) != 1:
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
