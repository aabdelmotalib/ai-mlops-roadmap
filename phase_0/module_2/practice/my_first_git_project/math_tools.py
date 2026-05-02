# Experimental: Division with error handling
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b
