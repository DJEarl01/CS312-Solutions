import random


def prime_test(N, k):
	# This is main function, that is connected to the Test button. You don't need to touch it.
	return fermat(N,k), miller_rabin(N,k)

def mod_exp(x, y, N):
    # You will need to implement this function and change the return value.   
    # Input: Two n−bit integers x and N, an integer exponent y
    # Output: x^y mod N

    # The total is O(n^3) because multiplication (O(n^2)) happens n times, so O(n(n^2))

    if y == 0: 
        return 1 # This is O(1) because it just spits out a value.
    else:
        z = mod_exp(x, y//2, N) # This recursion brings in O(n) because this occurs once per bit of Y
        if (y % 2 == 0):
            return ((z**2) % N) # z**2 is a multiplication, which is O(n^2)
        else:
            return ((x * (z**2)) % N)
	

def fprobability(k):
    # This function runs at a time of O(1) and returns a value corresponding to our spec for Fermat's Test   
    return 1 - (0.5**k)


def mprobability(k):
    # This function runs at a time of O(1) and returns a value corresponding to our spec for Miller-Rabin's Test  
    return 1 - (0.25**k)


def fermat(N,k):
    # A function that takes in a number N and a loop count k and returns whether N is prime or composite
    
    for i in range(k): # This for loop runs the test k times, coming out to a Time complexity of O(1)
        a = random.randint(1, N-1) # This pulls a random integer into the variable a for use with Fermat's theorem.
                                   # We'll assume this runs in O(1) time and takes no space.
        if (mod_exp(a, N-1, N) != 1): # If Fermat's thoorem is not satisfied, N is for sure composite.
            return 'composite'        # The Mod_Exp function runs in O(n^3) time
    
    else: # If we make it out of our loop through running Fermat's theorem and we still haven't failed, we conclude Primality.
	    return 'prime'


def miller_rabin(N,k):
    # A function that takes in a number N and a loop count k and returns whether N is prime or composite

    for i in range(k):          # This loop takes place k times, running at constant time.
        a = random.randint(1,N-1) # This pulls a random integer into the variable a for use with Fermat's theorem.
                                  # We'll assume this runs in O(1) time and takes no space.

        output = mod_exp(a, N-1, N) # This is our first primality test ran. It runs in O(n^3) time and O(n^2) space.
        if (output != 1):           # If our initial primality test fails, we return composite.
            return 'composite'
        M = (N-1)//2                # M is a placeholder for our modified exponent value. This and other divisions take O(n^2) time and O(n) space.
        
        while ((output == 1) and ((M % 2) == 0)): # So long as our output of the Mod_Exp function is 1 and our exponent is even, continue to loop through...
            output = mod_exp(a, M, N)             # This operation is our next primality test on the square-rooted version of our original equation.
            M //= 2                               # This operation takes O(n^3) time and O(n^2) space in total including the division operation.
        else:
            if ((output != 1) and (output != (N-1))): # At the end of our loop, our output value must be 1 or -1, or our number is composite. 
                                                      # When our Mod_Exp function mearns to return a -1, it actually returns N-1. 
                return 'composite'
    else: # If we make it out of our loop through running Fermat's theorem and we still haven't failed, we conclude Primality.
        return 'prime'