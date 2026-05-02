# Broken code example:
def calculate_average(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return average

def process_data(data):
    avg = calculate_average(data)
    return avg * 2

# Call it with bad data
result = process_data([]) # Empty list — division by zero!
print(result)