
class RSAKeyAgent:
    """Agent based on RSAKey from ..\Nyxion\env\Lib\site-packages\jose\backends\rsa_backend.py"""
    
    def __init__(self):
        self.name = "RSAKeyAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            SHA256 = 'SHA-256'
    SHA384 = 'SHA-384'
    SHA512 = 'SHA-512'
        if algorithm not in ALGORITHMS.RSA:
            raise JWKError('hash_alg: %s is not a valid hash algorithm' % algorithm)
        if algorithm in ALGORITHMS.RSA_KW and algorithm != ALGORITHMS.RSA1_5:
            raise JWKError('alg: %s is not supported by the RSA backend' % algorithm)
        self.hash_alg = {ALGORITHMS.RS256: self.SHA256, ALGORITHMS.RS384: self.SHA384, ALGORITHMS.RS512: self.SHA512}.get(algorithm)
        self._algorithm = algorithm
        if isinstance(key, dict):
            self._prepared_key = self._process_jwk(key)
            return
        if isinstance(key, (pyrsa.PublicKey, pyrsa.PrivateKey)):
            self._prepared_key = key
            return
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(key, bytes):
            try:
                self._prepared_key = pyrsa.PublicKey.load_pkcs1(key)
            except ValueError:
                try:
                    self._prepared_key = pyrsa.PublicKey.load_pkcs1_openssl_pem(key)
                except ValueError:
                    try:
                        self._prepared_key = pyrsa.PrivateKey.load_pkcs1(key)
                    except ValueError:
                        try:
                            der = pyrsa_pem.load_pem(key, b'PRIVATE KEY')
                            try:
                                pkcs1_key = rsa_private_key_pkcs8_to_pkcs1(der)
                            except PyAsn1Error:
                                pkcs1_key = _legacy_private_key_pkcs8_to_pkcs1(der)
                            self._prepared_key = pyrsa.PrivateKey.load_pkcs1(pkcs1_key, format='DER')
                        except ValueError as e:
                            raise JWKError(e)
            return
        raise JWKError('Unable to parse an RSA_JWK from key: %s' % key)
    def _process_jwk(self, jwk_dict):
        if not jwk_dict.get('kty') == 'RSA':
            raise JWKError("Incorrect key type. Expected: 'RSA', Received: %s" % jwk_dict.get('kty'))
        e = base64_to_long(jwk_dict.get('e'))
        n = base64_to_long(jwk_dict.get('n'))
        if 'd' not in jwk_dict:
            return pyrsa.PublicKey(e=e, n=n)
        else:
            d = base64_to_long(jwk_dict.get('d'))
            extra_params = ['p', 'q', 'dp', 'dq', 'qi']
            if any((k in jwk_dict for k in extra_params)):
                if not all((k in jwk_dict for k in extra_params)):
                    raise JWKError('Precomputed private key parameters are incomplete.')
                p = base64_to_long(jwk_dict['p'])
                q = base64_to_long(jwk_dict['q'])
                return pyrsa.PrivateKey(e=e, n=n, d=d, p=p, q=q)
            else:
                p, q = _rsa_recover_prime_factors(n, e, d)
                return pyrsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)
    def sign(self, msg):
        return pyrsa.sign(msg, self._prepared_key, self.hash_alg)
    def verify(self, msg, sig):
        if not self.is_public():
            warnings.warn('Attempting to verify a message with a private key. This is not recommended.')
        try:
            pyrsa.verify(msg, sig, self._prepared_key)
            return True
        except pyrsa.pkcs1.VerificationError:
            return False
    def is_public(self):
        return isinstance(self._prepared_key, pyrsa.PublicKey)
    def public_key(self):
        if isinstance(self._prepared_key, pyrsa.PublicKey):
            return self
        return self.__class__(pyrsa.PublicKey(n=self._prepared_key.n, e=self._prepared_key.e), self._algorithm)
    def to_pem(self, pem_format='PKCS8'):
        if isinstance(self._prepared_key, pyrsa.PrivateKey):
            der = self._prepared_key.save_pkcs1(format='DER')
            if pem_format == 'PKCS8':
                pkcs8_der = rsa_private_key_pkcs1_to_pkcs8(der)
                pem = pyrsa_pem.save_pem(pkcs8_der, pem_marker='PRIVATE KEY')
            elif pem_format == 'PKCS1':
                pem = pyrsa_pem.save_pem(der, pem_marker='RSA PRIVATE KEY')
            else:
                raise ValueError(f'Invalid pem format specified: {pem_format!r}')
        elif pem_format == 'PKCS8':
            pkcs1_der = self._prepared_key.save_pkcs1(format='DER')
            pkcs8_der = rsa_public_key_pkcs1_to_pkcs8(pkcs1_der)
            pem = pyrsa_pem.save_pem(pkcs8_der, pem_marker='PUBLIC KEY')
        elif pem_format == 'PKCS1':
            der = self._prepared_key.save_pkcs1(format='DER')
            pem = pyrsa_pem.save_pem(der, pem_marker='RSA PUBLIC KEY')
        else:
            raise ValueError(f'Invalid pem format specified: {pem_format!r}')
        return pem
    def to_dict(self):
        if not self.is_public():
            public_key = self.public_key()._prepared_key
        else:
            public_key = self._prepared_key
        data = {'alg': self._algorithm, 'kty': 'RSA', 'n': long_to_base64(public_key.n).decode('ASCII'), 'e': long_to_base64(public_key.e).decode('ASCII')}
        if not self.is_public():
            data.update({'d': long_to_base64(self._prepared_key.d).decode('ASCII'), 'p': long_to_base64(self._prepared_key.p).decode('ASCII'), 'q': long_to_base64(self._prepared_key.q).decode('ASCII'), 'dp': long_to_base64(self._prepared_key.exp1).decode('ASCII'), 'dq': long_to_base64(self._prepared_key.exp2).decode('ASCII'), 'qi': long_to_base64(self._prepared_key.coef).decode('ASCII')})
        return data
    def wrap_key(self, key_data):
        if not self.is_public():
            warnings.warn('Attempting to encrypt a message with a private key. This is not recommended.')
        wrapped_key = pyrsa.encrypt(key_data, self._prepared_key)
        return wrapped_key
    def unwrap_key(self, wrapped_key):
        try:
            unwrapped_key = pyrsa.decrypt(wrapped_key, self._prepared_key)
        except DecryptionError as e:
            raise JWEError(e)
        return unwrapped_key
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
