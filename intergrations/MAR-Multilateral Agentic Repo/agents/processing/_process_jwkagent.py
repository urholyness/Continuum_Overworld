
class _process_jwkAgent:
    """Agent based on _process_jwk from ..\Nyxion\env\Lib\site-packages\jose\backends\rsa_backend.py"""
    
    def __init__(self):
        self.name = "_process_jwkAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
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
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
