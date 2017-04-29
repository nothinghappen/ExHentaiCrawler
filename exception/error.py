class Networkerror(RuntimeError):
    def __init__(self,message):
        self.message = message

class ParseError(RuntimeError):
    def __init__(self,message):
        self.message = message