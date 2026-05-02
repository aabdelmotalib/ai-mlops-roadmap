# This script demonstrates lists and dictionaries
# LISTS: Ordered collections of items
colors = ['red', 'green', 'blue']
print(f'All colors: {colors}')
print(f'First color: {colors[0]}')

colors.append('yellow')
colors.remove('blue')
colors_count = len(colors)
print(f'Number of colors', colors_count)
print('colors in order: ')
for color in colors:
    print(f' - {color}')


# DICTIONARIES: Key-value pairs (labeled storage)
student = {
    'name': 'Ahmed Abdelmoteleb',
    'age': 28,
    'grade': "A",
    'courses': ['math', 'english', 'history']
}

print(f'\n Student info: {student}')
print(f'Name: {student["name"]}')
print(f'Age: {student["age"]}')
print(f'Courses: {student["courses"]}')

if 'age' in student:
    print(f'Student age is: {student["age"]}')

student['email'] = 'abdel@gmail.com'
print(f'After adding email: {student}')

student['grade'] = 'A+'
print(f'\n Student After grade: {student}')
print("\nStudent details:")
for key in student:
    value = student[key]
    print(f' {key}: {value}')

