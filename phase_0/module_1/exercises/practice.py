# Asks the user to enter a temperature in Celsius
try:
    ask_user = float(input("Enter a temperature in Celsius: "))

except ValueError:
    print("This is not a number!")

# Converts it to Fahrenheit using the formula: F = (C × 9/5) + 32
converter = (ask_user * 9/5) + 32

# Prints the result
result = converter
print(f"The temperature in Fahrenheit is: {result}")


