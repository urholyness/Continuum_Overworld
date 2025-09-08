
class _to_legacyAgent:
    """Agent based on _to_legacy from ..\Nyxion\env\Lib\site-packages\pip\_vendor\distlib\metadata.py"""
    
    def __init__(self):
        self.name = "_to_legacyAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            def process_entries(entries):
        reqts = set()
        for e in entries:
            extra = e.get('extra')
            env = e.get('environment')
            rlist = e['requires']
            for r in rlist:
                if not env and (not extra):
                    reqts.add(r)
                else:
                    marker = ''
                    if extra:
                        marker = 'extra == "%s"' % extra
                    if env:
                        if marker:
                            marker = '(%s) and %s' % (env, marker)
                        else:
                            marker = env
                    reqts.add(';'.join((r, marker)))
        return reqts
    assert self._data and (not self._legacy)
    result = LegacyMetadata()
    nmd = self._data
    for nk, ok in self.LEGACY_MAPPING.items():
        if not isinstance(nk, tuple):
            if nk in nmd:
                result[ok] = nmd[nk]
        else:
            d = nmd
            found = True
            for k in nk:
                try:
                    d = d[k]
                except (KeyError, IndexError):
                    found = False
                    break
            if found:
                result[ok] = d
    r1 = process_entries(self.run_requires + self.meta_requires)
    r2 = process_entries(self.build_requires + self.dev_requires)
    if self.extras:
        result['Provides-Extra'] = sorted(self.extras)
    result['Requires-Dist'] = sorted(r1)
    result['Setup-Requires-Dist'] = sorted(r2)
    return result
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
