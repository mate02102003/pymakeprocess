import typing

import makeprocess
makeprocess.LOGGING = True

class TestClass(makeprocess.MakeProcess):
    def __init__(self, i: int = 0):
        self.i = i
    
    def show(self: typing.Self) -> None:
        print(f"{self.__class__} {self.i = }")

class Test(makeprocess.MakeProcess):
    def __init__(self):
        print("Test")

if __name__ == "__main__":
    t1 = TestClass(1)
    t2 = Test()

    t1.show()

    t1.stop()
    t2.stop()
