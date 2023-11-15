class overall(object):
    def __init__(self):
        self.crimes ={ 'fur': 0,
        'drug': 0,
        'rap': 0,
        'kill': 0,
        'agg': 0,
        'spa': 0,
        'fire': 0}

    def set_crime(self, key, value):
            self.crimes[key] = self.crimes[key] + value

    def get_crime(self, key):
        return self.crimes[key]

    def get_crimes(self):
        return self.crimes
    
    def set_crimes(self,ov):
        self.crimes = ov.get_crimes()

    def update_crimes(self, ov):
        for k, v in self.crimes.items():
            self.crimes[k] = v + ov.get_crime(k)

class way(overall):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.crimes ={ 'fur': 0,
        'drug': 0,
        'rap': 0,
        'kill': 0,
        'agg': 0,
        'spa': 0,
        'fire': 0}
        
    def get_start(self):
        return self.start
    
    def get_end(self):
        return self.end
    
    