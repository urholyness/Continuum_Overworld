
class HMACKeyAgent:
    """Agent based on HMACKey from ..\Nyxion\env\Lib\site-packages\jose\backends\native.py"""
    
    def __init__(self):
        self.name = "HMACKeyAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Performs signing and verification operations using HMAC
    and the specified hash function.
    """
    HASHES = {ALGORITHMS.HS256: hashlib.sha256, ALGORITHMS.HS384: hashlib.sha384, ALGORITHMS.HS512: hashlib.sha512}
        if algorithm not in ALGORITHMS.HMAC:
            raise JWKError('hash_alg: %s is not a valid hash algorithm' % algorithm)
        self._algorithm = algorithm
        self._hash_alg = self.HASHES.get(algorithm)
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
    def sign(self, msg):
        return hmac.new(self.prepared_key, msg, self._hash_alg).digest()
    def verify(self, msg, sig):
        return hmac.compare_digest(sig, self.sign(msg))
    def to_dict(self):
        return {'alg': self._algorithm, 'kty': 'oct', 'k': base64url_encode(self.prepared_key).decode('ASCII')}
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
