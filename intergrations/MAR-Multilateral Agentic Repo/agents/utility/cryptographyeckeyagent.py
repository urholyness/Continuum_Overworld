
class CryptographyECKeyAgent:
    """Agent based on CryptographyECKey from ..\Nyxion\env\Lib\site-packages\jose\backends\cryptography_backend.py"""
    
    def __init__(self):
        self.name = "CryptographyECKeyAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            SHA256 = hashes.SHA256
    SHA384 = hashes.SHA384
    SHA512 = hashes.SHA512
        if algorithm not in ALGORITHMS.EC:
            raise JWKError('hash_alg: %s is not a valid hash algorithm' % algorithm)
        self.hash_alg = {ALGORITHMS.ES256: self.SHA256, ALGORITHMS.ES384: self.SHA384, ALGORITHMS.ES512: self.SHA512}.get(algorithm)
        self._algorithm = algorithm
        self.cryptography_backend = cryptography_backend
        if hasattr(key, 'public_bytes') or hasattr(key, 'private_bytes'):
            self.prepared_key = key
            return
        if hasattr(key, 'to_pem'):
            key = key.to_pem().decode('utf-8')
        if isinstance(key, dict):
            self.prepared_key = self._process_jwk(key)
            return
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(key, bytes):
            try:
                try:
                    key = load_pem_public_key(key, self.cryptography_backend())
                except ValueError:
            except Exception as e:
                raise JWKError(e)
            self.prepared_key = key
            return
        raise JWKError('Unable to parse an ECKey from key: %s' % key)
    def _process_jwk(self, jwk_dict):
        if not jwk_dict.get('kty') == 'EC':
            raise JWKError("Incorrect key type. Expected: 'EC', Received: %s" % jwk_dict.get('kty'))
        if not all((k in jwk_dict for k in ['x', 'y', 'crv'])):
            raise JWKError('Mandatory parameters are missing')
        x = base64_to_long(jwk_dict.get('x'))
        y = base64_to_long(jwk_dict.get('y'))
        curve = {'P-256': ec.SECP256R1, 'P-384': ec.SECP384R1, 'P-521': ec.SECP521R1}[jwk_dict['crv']]
        public = ec.EllipticCurvePublicNumbers(x, y, curve())
        if 'd' in jwk_dict:
            d = base64_to_long(jwk_dict.get('d'))
            private = ec.EllipticCurvePrivateNumbers(d, public)
            return private.private_key(self.cryptography_backend())
        else:
            return public.public_key(self.cryptography_backend())
    def _sig_component_length(self):
        """Determine the correct serialization length for an encoded signature component.
        This is the number of bytes required to encode the maximum key value.
        """
        return int(math.ceil(self.prepared_key.key_size / 8.0))
    def _der_to_raw(self, der_signature):
        """Convert signature from DER encoding to RAW encoding."""
        r, s = decode_dss_signature(der_signature)
        component_length = self._sig_component_length()
        return int_to_bytes(r, component_length) + int_to_bytes(s, component_length)
    def _raw_to_der(self, raw_signature):
        """Convert signature from RAW encoding to DER encoding."""
        component_length = self._sig_component_length()
        if len(raw_signature) != int(2 * component_length):
            raise ValueError('Invalid signature')
        r_bytes = raw_signature[:component_length]
        s_bytes = raw_signature[component_length:]
        r = int.from_bytes(r_bytes, 'big')
        s = int.from_bytes(s_bytes, 'big')
        return encode_dss_signature(r, s)
    def sign(self, msg):
        if self.hash_alg.digest_size * 8 > self.prepared_key.curve.key_size:
            raise TypeError('this curve (%s) is too short for your digest (%d)' % (self.prepared_key.curve.name, 8 * self.hash_alg.digest_size))
        signature = self.prepared_key.sign(msg, ec.ECDSA(self.hash_alg()))
        return self._der_to_raw(signature)
    def verify(self, msg, sig):
        try:
            signature = self._raw_to_der(sig)
            self.prepared_key.verify(signature, msg, ec.ECDSA(self.hash_alg()))
            return True
        except Exception:
            return False
    def is_public(self):
        return hasattr(self.prepared_key, 'public_bytes')
    def public_key(self):
        if self.is_public():
            return self
        return self.__class__(self.prepared_key.public_key(), self._algorithm)
    def to_pem(self):
        if self.is_public():
            pem = self.prepared_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            return pem
        pem = self.prepared_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
        return pem
    def to_dict(self):
        if not self.is_public():
            public_key = self.prepared_key.public_key()
        else:
            public_key = self.prepared_key
        crv = {'secp256r1': 'P-256', 'secp384r1': 'P-384', 'secp521r1': 'P-521'}[self.prepared_key.curve.name]
        key_size = (self.prepared_key.curve.key_size + 7) // 8
        data = {'alg': self._algorithm, 'kty': 'EC', 'crv': crv, 'x': long_to_base64(public_key.public_numbers().x, size=key_size).decode('ASCII'), 'y': long_to_base64(public_key.public_numbers().y, size=key_size).decode('ASCII')}
        if not self.is_public():
            private_value = self.prepared_key.private_numbers().private_value
            data['d'] = long_to_base64(private_value, size=key_size).decode('ASCII')
        return data
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
