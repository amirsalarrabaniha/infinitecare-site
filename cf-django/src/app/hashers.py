"""Pyodide's hashlib has no pbkdf2_hmac/scrypt (no OpenSSL), so provide a pure-Python PBKDF2-SHA256 hasher.
Iterations are lower than Django's default to stay within Workers CPU limits."""
import base64
import hashlib
import hmac
import struct

from django.contrib.auth.hashers import PBKDF2PasswordHasher


def _pbkdf2_sha256(password: bytes, salt: bytes, iterations: int, dklen: int = 32) -> bytes:
    inner, outer = hashlib.sha256(), hashlib.sha256()
    key = password if len(password) <= 64 else hashlib.sha256(password).digest()
    key = key.ljust(64, b"\0")
    inner.update(bytes(b ^ 0x36 for b in key))
    outer.update(bytes(b ^ 0x5C for b in key))

    def prf(msg):
        i, o = inner.copy(), outer.copy()
        i.update(msg)
        o.update(i.digest())
        return o.digest()

    out = b""
    block = 1
    while len(out) < dklen:
        u = prf(salt + struct.pack(">I", block))
        acc = int.from_bytes(u, "big")
        for _ in range(iterations - 1):
            u = prf(u)
            acc ^= int.from_bytes(u, "big")
        out += acc.to_bytes(32, "big")
        block += 1
    return out[:dklen]


class PurePythonPBKDF2Hasher(PBKDF2PasswordHasher):
    algorithm = "pbkdf2_sha256_py"
    iterations = 60000

    def encode(self, password, salt, iterations=None):
        self._check_encode_args(password, salt)
        iterations = iterations or self.iterations
        h = _pbkdf2_sha256(password.encode(), salt.encode(), iterations)
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, base64.b64encode(h).decode("ascii").strip())
