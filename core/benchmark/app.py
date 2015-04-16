class App:
     def __init__(self,name,key=None):
          self.name = name
          if key == None:
               self.key = name
          else:
               self.key = key 
