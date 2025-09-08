
class CryptographyHMACKeyAgent:
    """Agent based on CryptographyHMACKey from ..\Nyxion\env\Lib\site-packages\jose\backends\cryptography_backend.py"""
    
    def __init__(self):
        self.name = "CryptographyHMACKeyAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Performs signing and verification operations using HMAC
    and the specified hash function.
    """
    ALG_MAP = {ALGORITHMS.HS256: hashes.SHA256(), ALGORITHMS.HS384: hashes.SHA384(), ALGORITHMS.HS512: hashes.SHA512()}
        if algorithm not in ALGORITHMS.HMAC:
            raise JWKError('hash_alg: %s is not a valid hash algorithm' % algorithm)
        self._algorithm = algorithm
        self._hash_alg = self.ALG_MAP.get(algorithm)
        if isinstance(key, dict):
            self.prepared_key = self._process_jwk(key)
            return
        if not isinstance(key, str) and (not isinstance(key, bytes)):
            raise JWKError('Expecting a string- or bytes-formatted key.')
        if isinstance(key, str):
            key = key.encode('utf-8')
        if is_pem_format(key) or is_ssh_key(key):
            raise JWKError('The specified key is an asymmetric key or x509 certificate and should not be used as an HMAC secret.')
        self.prepared_key = key
    def _process_jwk(self, jwk_dict):
        if not jwk_dict.get('kty') == 'oct':
            raise JWKError("Incorrect key type. Expected: 'oct', Received: %s" % jwk_dict.get('kty'))
        k = jwk_dict.get('k')
        k = k.encode('utf-8')
        k = bytes(k)
        k = base64url_decode(k)
        return k
    def to_dict(self):
        return {'alg': self._algorithm, 'kty': 'oct', 'k': base64url_encode(self.prepared_key).decode('ASCII')}
    def sign(self, msg):
        msg = ensure_binary(msg)
        h = hmac.HMAC(self.prepared_key, self._hash_alg, backend=default_backend())
        h.update(msg)
        signature = h.finalize()
        return signature
    def verify(self, msg, sig):
        msg = ensure_binary(msg)
        sig = ensure_binary(sig)
        h = hmac.HMAC(self.prepared_key, self._hash_alg, backend=default_backend())
        h.update(msg)
        try:
            h.verify(sig)
            verified = True
        except InvalidSignature:
            verified = False
        return verified
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
