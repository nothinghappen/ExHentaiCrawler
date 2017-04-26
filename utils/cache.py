import collections

class cache:
    maxSize = 0
    deque = collections.deque()
    dic = {}

    def __init__(self,maxSize = 100):
        self.maxSize = maxSize

    def put(self,key,val):
        if len(self.dic) == self.maxSize:
            deleteKey = self.deque.popleft()
            del self.dic[deleteKey]
        self.dic[key] = val
        self.deque.append(key)

    def get(self,key):
        if key not in self.dic:
            return None
        else:
            return self.dic[key]

    def clear(self):
        self.dic.clear()
        self.deque.clear()

    def containKey(self,key):
        if key not in self.dic:
            return False
        else:
            return True
        


