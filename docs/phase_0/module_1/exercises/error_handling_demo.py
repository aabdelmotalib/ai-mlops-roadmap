# This script demonstrates how to handle errors gracefully
# EXAMPLE 1: Handle division by zero
print("=== EXAMPLE 1: Division by Zero ===")
try:
    numerator = 10
    denominator = 0
    result = numerator / denominator
    print(f'{numerator} / {denominator} = {result}')
except ZeroDivisionError:
    print(f'ERROR: You cannot divide by zero!')
    denominator = 2
    result = numerator / denominator
    print(f'{numerator} / {denominator} = {result}')


# EXAMPLE 2: Handle invalid input
print("\n=== EXAMPLE 2: Invalid Input ===")
try: 
    user_input = input("Enter a number: ")
    # Convert the input to an integer (this might fail if they type letters)
    number = int(user_input)
    print(f"You entered number: {number}")
    print(f'Doubled: {number * 2 }')
except ValueError:
    print('ERROR: the number is not valid !')
    print('You need to enter only digits.')


# EXAMPLE 3: Handle file not found
print("\n=== EXAMPLE 3: File Not Found ===")
try:
    filename = 'nonexistent_file.txt'
    with open (filename, 'r') as file:
        content = file.read()
        print(content)
except FileNotFoundError:
    print(f'ERROR: the file {filename} does not exist!')
    print("Please create the file first.")


# EXAMPLE 4: Handle multiple types of errors
print("\n=== EXAMPLE 4: Multiple Error Types ===")
try:
    numbers = [1,2,3]
    index = 10
    number = numbers[index]
    print(number)
except IndexError:
    print("ERROR: that position does not exist!")
except ValueError:
    print("ERROR: Invalid value!")


# EXAMPLE 5: Generic error handling (catch anything)
print("\n=== EXAMPLE 5: Generic Error Handling ===")
try:
    result = 10 + "Hello"
except:
    print("ERROR: something went wrong!")
    print("We cannot use bare expect in real code.")

