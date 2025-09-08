
class NumPyLexerAgent:
    """Agent based on NumPyLexer from ..\Nyxion\env\Lib\site-packages\pip\_vendor\pygments\lexers\python.py"""
    
    def __init__(self):
        self.name = "NumPyLexerAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    A Python lexer recognizing Numerical Python builtins.
    """
    name = 'NumPy'
    url = 'https://numpy.org/'
    aliases = ['numpy']
    version_added = '0.10'
    mimetypes = []
    filenames = []
    EXTRA_KEYWORDS = {'abs', 'absolute', 'accumulate', 'add', 'alen', 'all', 'allclose', 'alltrue', 'alterdot', 'amax', 'amin', 'angle', 'any', 'append', 'apply_along_axis', 'apply_over_axes', 'arange', 'arccos', 'arccosh', 'arcsin', 'arcsinh', 'arctan', 'arctan2', 'arctanh', 'argmax', 'argmin', 'argsort', 'argwhere', 'around', 'array', 'array2string', 'array_equal', 'array_equiv', 'array_repr', 'array_split', 'array_str', 'arrayrange', 'asanyarray', 'asarray', 'asarray_chkfinite', 'ascontiguousarray', 'asfarray', 'asfortranarray', 'asmatrix', 'asscalar', 'astype', 'atleast_1d', 'atleast_2d', 'atleast_3d', 'average', 'bartlett', 'base_repr', 'beta', 'binary_repr', 'bincount', 'binomial', 'bitwise_and', 'bitwise_not', 'bitwise_or', 'bitwise_xor', 'blackman', 'bmat', 'broadcast', 'byte_bounds', 'bytes', 'byteswap', 'c_', 'can_cast', 'ceil', 'choose', 'clip', 'column_stack', 'common_type', 'compare_chararrays', 'compress', 'concatenate', 'conj', 'conjugate', 'convolve', 'copy', 'corrcoef', 'correlate', 'cos', 'cosh', 'cov', 'cross', 'cumprod', 'cumproduct', 'cumsum', 'delete', 'deprecate', 'diag', 'diagflat', 'diagonal', 'diff', 'digitize', 'disp', 'divide', 'dot', 'dsplit', 'dstack', 'dtype', 'dump', 'dumps', 'ediff1d', 'empty', 'empty_like', 'equal', 'exp', 'expand_dims', 'expm1', 'extract', 'eye', 'fabs', 'fastCopyAndTranspose', 'fft', 'fftfreq', 'fftshift', 'fill', 'finfo', 'fix', 'flat', 'flatnonzero', 'flatten', 'fliplr', 'flipud', 'floor', 'floor_divide', 'fmod', 'frexp', 'fromarrays', 'frombuffer', 'fromfile', 'fromfunction', 'fromiter', 'frompyfunc', 'fromstring', 'generic', 'get_array_wrap', 'get_include', 'get_numarray_include', 'get_numpy_include', 'get_printoptions', 'getbuffer', 'getbufsize', 'geterr', 'geterrcall', 'geterrobj', 'getfield', 'gradient', 'greater', 'greater_equal', 'gumbel', 'hamming', 'hanning', 'histogram', 'histogram2d', 'histogramdd', 'hsplit', 'hstack', 'hypot', 'i0', 'identity', 'ifft', 'imag', 'index_exp', 'indices', 'inf', 'info', 'inner', 'insert', 'int_asbuffer', 'interp', 'intersect1d', 'intersect1d_nu', 'inv', 'invert', 'iscomplex', 'iscomplexobj', 'isfinite', 'isfortran', 'isinf', 'isnan', 'isneginf', 'isposinf', 'isreal', 'isrealobj', 'isscalar', 'issctype', 'issubclass_', 'issubdtype', 'issubsctype', 'item', 'itemset', 'iterable', 'ix_', 'kaiser', 'kron', 'ldexp', 'left_shift', 'less', 'less_equal', 'lexsort', 'linspace', 'load', 'loads', 'loadtxt', 'log', 'log10', 'log1p', 'log2', 'logical_and', 'logical_not', 'logical_or', 'logical_xor', 'logspace', 'lstsq', 'mat', 'matrix', 'max', 'maximum', 'maximum_sctype', 'may_share_memory', 'mean', 'median', 'meshgrid', 'mgrid', 'min', 'minimum', 'mintypecode', 'mod', 'modf', 'msort', 'multiply', 'nan', 'nan_to_num', 'nanargmax', 'nanargmin', 'nanmax', 'nanmin', 'nansum', 'ndenumerate', 'ndim', 'ndindex', 'negative', 'newaxis', 'newbuffer', 'newbyteorder', 'nonzero', 'not_equal', 'obj2sctype', 'ogrid', 'ones', 'ones_like', 'outer', 'permutation', 'piecewise', 'pinv', 'pkgload', 'place', 'poisson', 'poly', 'poly1d', 'polyadd', 'polyder', 'polydiv', 'polyfit', 'polyint', 'polymul', 'polysub', 'polyval', 'power', 'prod', 'product', 'ptp', 'put', 'putmask', 'r_', 'randint', 'random_integers', 'random_sample', 'ranf', 'rank', 'ravel', 'real', 'real_if_close', 'recarray', 'reciprocal', 'reduce', 'remainder', 'repeat', 'require', 'reshape', 'resize', 'restoredot', 'right_shift', 'rint', 'roll', 'rollaxis', 'roots', 'rot90', 'round', 'round_', 'row_stack', 's_', 'sample', 'savetxt', 'sctype2char', 'searchsorted', 'seed', 'select', 'set_numeric_ops', 'set_printoptions', 'set_string_function', 'setbufsize', 'setdiff1d', 'seterr', 'seterrcall', 'seterrobj', 'setfield', 'setflags', 'setmember1d', 'setxor1d', 'shape', 'show_config', 'shuffle', 'sign', 'signbit', 'sin', 'sinc', 'sinh', 'size', 'slice', 'solve', 'sometrue', 'sort', 'sort_complex', 'source', 'split', 'sqrt', 'square', 'squeeze', 'standard_normal', 'std', 'subtract', 'sum', 'svd', 'swapaxes', 'take', 'tan', 'tanh', 'tensordot', 'test', 'tile', 'tofile', 'tolist', 'tostring', 'trace', 'transpose', 'trapz', 'tri', 'tril', 'trim_zeros', 'triu', 'true_divide', 'typeDict', 'typename', 'uniform', 'union1d', 'unique', 'unique1d', 'unravel_index', 'unwrap', 'vander', 'var', 'vdot', 'vectorize', 'view', 'vonmises', 'vsplit', 'vstack', 'weibull', 'where', 'who', 'zeros', 'zeros_like'}
    def get_tokens_unprocessed(self, text):
        for index, token, value in PythonLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.EXTRA_KEYWORDS:
                yield (index, Keyword.Pseudo, value)
            else:
                yield (index, token, value)
    def analyse_text(text):
        ltext = text[:1000]
        return (shebang_matches(text, 'pythonw?(3(\\.\\d)?)?') or 'import ' in ltext) and ('import numpy' in ltext or 'from numpy import' in ltext)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
