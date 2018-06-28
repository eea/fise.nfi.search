import math
import hashlib

# Vowels removed to avoid accidental offensive words
ALPHABET = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
LOWER_ALPHABET = 'bcdfghjklmnpqrstvwxyz'


def hash_index(index, hash_key):
    i = list(index)
    passhash = hashlib.sha256(hash_key).hexdigest()
    passhash = hashlib.sha512(hash_key).hexdigest() if len(passhash) < len(index) else passhash
    p = list(passhash)[0:len(index)]
    index = ''.join(
        list(zip(*sorted(zip(p, i))))[1]
    )
    return index


def id_to_alpha(id_num, pad_to=None, alphabet=None, hash_key=None):
    index = alphabet or ALPHABET
    if hash_key is not None:
        index = hash_index(index, hash_key)

    base = len(index)

    if pad_to is not None:
        pad_to -= 1
        if pad_to > 0:
            id_num += int(pow(base, pad_to))

    out = []
    t = int(math.log(id_num, base))
    while True:
        bcp = int(pow(base, t))
        a = int(id_num / bcp) % base
        out.append(index[a:a + 1])
        id_num = id_num - (a * bcp)
        t -= 1
        if t < 0:
            break

    out = ''.join(out[::-1])
    return out


def alpha_to_id(id_num, pad_to=False, alphabet=None, hash_key=None):
    index = alphabet or ALPHABET
    if hash_key is not None:
        index = hash_index(index, hash_key)

    base = len(index)

    id_num = id_num[::-1]
    out = 0
    length = len(id_num) - 1
    t = 0
    while True:
        bcpow = int(pow(base, length - t))
        out = out + index.index(id_num[t:t + 1]) * bcpow
        t += 1
        if t > length:
            break

    if pad_to is not None:
        pad_to -= 1
        if pad_to > 0:
            out -= int(pow(base, pad_to))

    return out
