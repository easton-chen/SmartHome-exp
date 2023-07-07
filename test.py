global a
a = 1

def fun1():
    print(a)

def fun():
    global a
    a = 2
    print(a)

fun1()
fun()
fun1()