# This script demonstrates how to write and use functions
# FUNCTION 1: A simple greeting function
def greet(name):
    message = 'Hello,' + name + '! Welcome to Python!'
    return message
result = greet('Ahmed Abdel')
print (result)

# FUNCTION 2: A function that does math
def add_numbers(num1, num2):
    total = num1 + num2
    return total
sum_result = add_numbers(50, 25)
print(f'50 + 25 = {sum_result}')

# FUNCTION 3: A function that checks if someone is an adult
def is_adult(age):
    if age >= 18:
        return True
    else:
        return False
if is_adult(25):
    print('Ahmed is Adult')
else:
    print('Ahmed is not an adult')

# FUNCTION 4: A function that doesn't return anything
def print_multiplied(num, times):
    for i in range(times):
        result = num * (i + 1)
        print(f'{num} * {i + 1} = {result}')
print_multiplied(3, 5)

