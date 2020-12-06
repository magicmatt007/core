# from testTEMP3 import testTEMP3
# from testTEMP3 import TestTEMP3


class ConfigEntry():
    def __init__(self):
        self.surname = "Miller"
        self.givenname = "Max"

    def print_my_name(self):
        """
        docstring
        """
        print(f"My name is {self.givenname} {self.surname}")

        obj2 = TestTEMP3()
        obj2.setup_something("Hello",self)




class TestTEMP3:
    def __init__(self):
        print("Hello from TestTEMP3")

    def setup_something(self,arg1, entry, extra):
        print(f"arg1: {arg1}")
        print(f"entry: {entry}")
        print(f"extra: {extra}")

obj=ConfigEntry()
obj.print_my_name()





