> [!WARNING]
> The library is not in production ready state yet

# Summary
In Python you can't easily send functions through pipes, because they are not pickleable,
so that's how this little module came together by hacking the functions ```__code__``` attributum

It automaticly changes out the classes ```__init__``` function and your defined functions.

*NOTE: This small module was created for my own need!*

# Includes
1. class MakeProcess:
    - subclass to turn class into a process
2. LOGGING constant (default False)
    - turn logging on and off

# TODO
- add special case funtions list to change out
- test in real example