import PyQt6
print('Testing Environment')

def multiply(x,y):
    if y < 1:
        return 0
    z = multiply (x, (y//2))
    if (y%2 == 0):
        return 2*z
    else:
        return x + (2*z)

num1 = 8916846813516848798465132135468498985618468768165135846513565135184845135
num2 = 5846654654654548981651351698498165498465651654984515849881351684681351684

print("{:d} x {:d} = {:d}".format(num1, num2, multiply(num1, num2)))