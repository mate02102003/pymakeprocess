"""
This module is a hack for Python-s classes so you can easily make them run in seperate processes
without change how you define them and call their methods in your own code
"""

import multiprocessing
import multiprocessing.connection
import types
import typing

LOGGING: bool = False

CO_NAMES: typing.Final[tuple[str]] = (
    "co_argcount",
    "co_posonlyargcount",
    "co_kwonlyargcount",
    "co_nlocals",
    "co_stacksize",
    "co_flags",
    "co_firstlineno",
    "co_code",
    "co_consts",
    "co_names",
    "co_varnames",
    "co_freevars",
    "co_cellvars",
    "co_filename",
    "co_name",
    "co_qualname",
    "co_linetable",
    "co_exceptiontable",
)

def get_func_code_attributes(func: types.FunctionType) -> dict[str, typing.Any]:
    attrs = {}

    for co in CO_NAMES:
        attrs[co] = getattr(func.__code__, co)

    return attrs

class Object:
    def __init__(self):
        ...

    def _dumy(self) -> None:
        ...

class MakeProcess(multiprocessing.Process):
    this: type[typing.Self] | Object

    DESTROY_MESSAGE: str = "DESTROY-OBJECT"

    pipe_main_recv: multiprocessing.connection.PipeConnection
    pipe_main_send: multiprocessing.connection.PipeConnection
    pipe_fork_recv: multiprocessing.connection.PipeConnection
    pipe_fork_send: multiprocessing.connection.PipeConnection

    def __init__(self: typing.Self, cls_init_code_attrs: types.FunctionType, *args: tuple[typing.Any, ...], **kwargs: dict[str, typing.Any]):
        super().__init__()

        self.cls_init_code_attrs = cls_init_code_attrs
        self.args = args
        self.kwargs = kwargs

        self.pipe_main_recv, self.pipe_main_send = multiprocessing.Pipe(duplex=False)
        self.pipe_fork_recv, self.pipe_fork_send = multiprocessing.Pipe(duplex=False)
    
    def run(self: typing.Self) -> None:
        if LOGGING: print("INFO:", f"STARTING PROCESS pid({self.pid})")

        Object.__init__.__code__ = Object.__init__.__code__.replace(**self.cls_init_code_attrs)
        self.this = Object(*self.args, **self.kwargs)

        while (func_code_data:=self.pipe_main_recv.recv()) != self.DESTROY_MESSAGE:
            Object._dumy.__code__ = Object._dumy.__code__.replace(**func_code_data)

            args:  tuple[typing.Any, ...] = self.pipe_main_recv.recv()
            kwargs: dict[str, typing.Any] = self.pipe_main_recv.recv()

            self.pipe_fork_send.send(Object._dumy(self.this, *args, **kwargs))
        
        if LOGGING: print("INFO:", f"CLOSING PROCESS pid({self.pid})")
    
    def stop(self: typing.Self) -> None:
        self.pipe_main_send.send(self.DESTROY_MESSAGE)
            
    def __init_subclass__(cls: type[typing.Self]):
        cls_init_code_attrs = get_func_code_attributes(cls.__init__)

        def init(self: typing.Self, *args, **kwargs) -> None:
            MakeProcess.__init__(self, cls_init_code_attrs, *args, **kwargs)
            self.start()
        
        cls.__init__ = init

        cls_methods = filter(
            lambda cls_attr: isinstance(cls_attr, types.FunctionType),
            map(
                lambda name: getattr(cls, name),
                filter(lambda key: key not in dir(MakeProcess), dir(cls))
            )
        )
        for cls_method in cls_methods:
            method_code_data = get_func_code_attributes(cls_method)

            def method(self: typing.Self, *args, **kwargs) -> typing.Any:
                local_method_code_data = method_code_data.copy()

                self.pipe_main_send.send(local_method_code_data)
                self.pipe_main_send.send(args)
                self.pipe_main_send.send(kwargs)

                return self.pipe_fork_recv.recv()
            
            setattr(cls, cls_method.__name__, method)
