
class CryptographyRSAKeyAgent:
    """Agent based on CryptographyRSAKey from ..\Nyxion\env\Lib\site-packages\jose\backends\cryptography_backend.py"""
    
    def __init__(self):
        self.name = "CryptographyRSAKeyAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            SHA256 = hashes.SHA256
    SHA384 = hashes.SHA384
    SHA512 = hashes.SHA512
    RSA1_5 = padding.PKCS1v15()
    RSA_OAEP = padding.OAEP(padding.MGF1(hashes.SHA1()), hashes.SHA1(), None)
    RSA_OAEP_256 = padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None)
        if algorithm not in ALGORITHMS.RSA:
            raise JWKError('hash_alg: %s is not a valid hash algorithm' % algorithm)
        self.hash_alg = {ALGORITHMS.RS256: self.SHA256, ALGORITHMS.RS384: self.SHA384, ALGORITHMS.RS512: self.SHA512}.get(algorithm)
        self._algorithm = algorithm
        self.padding = {ALGORITHMS.RSA1_5: self.RSA1_5, ALGORITHMS.RSA_OAEP: self.RSA_OAEP, ALGORITHMS.RSA_OAEP_256: self.RSA_OAEP_256}.get(algorithm)
        self.cryptography_backend = cryptography_backend
        if hasattr(key, 'public_bytes') and hasattr(key, 'public_numbers') or hasattr(key, 'private_bytes'):
            self.prepared_key = key
            return
        if isinstance(key, dict):
            self.prepared_key = self._process_jwk(key)
            return
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(key, bytes):
            try:
                if key.startswith(b'-----BEGIN CERTIFICATE-----'):
                    self._process_cert(key)
                    return
                try:
                    self.prepared_key = load_pem_public_key(key, self.cryptography_backend())
                except ValueError:
            except Exception as e:
                raise JWKError(e)
            return
        raise JWKError('Unable to parse an RSA_JWK from key: %s' % key)
    def _process_jwk(self, jwk_dict):
        if not jwk_dict.get('kty') == 'RSA':
            raise JWKError("Incorrect key type. Expected: 'RSA', Received: %s" % jwk_dict.get('kty'))
        e = base64_to_long(jwk_dict.get('e', 256))
        n = base64_to_long(jwk_dict.get('n'))
        public = rsa.RSAPublicNumbers(e, n)
        if 'd' not in jwk_dict:
            return public.public_key(self.cryptography_backend())
        else:
            d = base64_to_long(jwk_dict.get('d'))
            extra_params = ['p', 'q', 'dp', 'dq', 'qi']
            if any((k in jwk_dict for k in extra_params)):
                if not all((k in jwk_dict for k in extra_params)):
                    raise JWKError('Precomputed private key parameters are incomplete.')
                p = base64_to_long(jwk_dict['p'])
                q = base64_to_long(jwk_dict['q'])
                dp = base64_to_long(jwk_dict['dp'])
                dq = base64_to_long(jwk_dict['dq'])
                qi = base64_to_long(jwk_dict['qi'])
            else:
                p, q = rsa.rsa_recover_prime_factors(n, e, d)
                dp = rsa.rsa_crt_dmp1(d, p)
                dq = rsa.rsa_crt_dmq1(d, q)
                qi = rsa.rsa_crt_iqmp(p, q)
            private = rsa.RSAPrivateNumbers(p, q, d, dp, dq, qi, public)
            return private.private_key(self.cryptography_backend())
    def _process_cert(self, key):
        key = load_pem_x509_certificate(key, self.cryptography_backend())
        self.prepared_key = key.public_key()
    def sign(self, msg):
        try:
            signature = self.prepared_key.sign(msg, padding.PKCS1v15(), self.hash_alg())
        except Exception as e:
            raise JWKError(e)
        return signature
    def verify(self, msg, sig):
        if not self.is_public():
            warnings.warn('Attempting to verify a message with a private key. This is not recommended.')
        try:
            self.public_key().prepared_key.verify(sig, msg, padding.PKCS1v15(), self.hash_alg())
            return True
        except InvalidSignature:
            return False
    def is_public(self):
        return hasattr(self.prepared_key, 'public_bytes')
    def public_key(self):
        if self.is_public():
            return self
        return self.__class__(self.prepared_key.public_key(), self._algorithm)
    def to_pem(self, pem_format='PKCS8'):
        if self.is_public():
            if pem_format == 'PKCS8':
                fmt = serialization.PublicFormat.SubjectPublicKeyInfo
            elif pem_format == 'PKCS1':
                fmt = serialization.PublicFormat.PKCS1
            else:
                raise ValueError('Invalid format specified: %r' % pem_format)
            pem = self.prepared_key.public_bytes(encoding=serialization.Encoding.PEM, format=fmt)
            return pem
        if pem_format == 'PKCS8':
            fmt = serialization.PrivateFormat.PKCS8
        elif pem_format == 'PKCS1':
            fmt = serialization.PrivateFormat.TraditionalOpenSSL
        else:
            raise ValueError('Invalid format specified: %r' % pem_format)
        return self.prepared_key.private_bytes(encoding=serialization.Encoding.PEM, format=fmt, encryption_algorithm=serialization.NoEncryption())
    def to_dict(self):
        if not self.is_public():
            public_key = self.prepared_key.public_key()
        else:
            public_key = self.prepared_key
        data = {'alg': self._algorithm, 'kty': 'RSA', 'n': long_to_base64(public_key.public_numbers().n).decode('ASCII'), 'e': long_to_base64(public_key.public_numbers().e).decode('ASCII')}
        if not self.is_public():
            data.update({'d': long_to_base64(self.prepared_key.private_numbers().d).decode('ASCII'), 'p': long_to_base64(self.prepared_key.private_numbers().p).decode('ASCII'), 'q': long_to_base64(self.prepared_key.private_numbers().q).decode('ASCII'), 'dp': long_to_base64(self.prepared_key.private_numbers().dmp1).decode('ASCII'), 'dq': long_to_base64(self.prepared_key.private_numbers().dmq1).decode('ASCII'), 'qi': long_to_base64(self.prepared_key.private_numbers().iqmp).decode('ASCII')})
        return data
    def wrap_key(self, key_data):
        try:
            wrapped_key = self.prepared_key.encrypt(key_data, self.padding)
        except Exception as e:
            raise JWEError(e)
        return wrapped_key
    def unwrap_key(self, wrapped_key):
        try:
            unwrapped_key = self.prepared_key.decrypt(wrapped_key, self.padding)
            return unwrapped_key
        except Exception as e:
            raise JWEError(e)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
