'''
Serve a salvare un template così da non dover ricaricare tutto ogni volta che cambiamo pagina
'''

class template(object):
    def __init__(self):
        self.string = ''

    def get_string(self):
        return self.string
    
    def set_string(self, string):
        self.string = string