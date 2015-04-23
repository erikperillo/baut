class FilteringException(Exception):
     def __init__(self,message):
          super(FilteringException,self).__init__(message)
          pass

class ExtractingException(Exception):
     def __init__(self,message):
          super(ExtractingException,self).__init__(message)
          pass
