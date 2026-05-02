# This script demonstrates reading and writing files
# READ A FILE
print("=== READING A FILE ===")
with open('sample.txt', 'r') as file:
    content = file.read()
    print('Full Content: ')
    print(content)

# READ A FILE LINE BY LINE
print("\n=== READING LINE BY LINE ===")
with open('sample.txt', 'r') as file:
    for line in file:
        print(f'Line: {line.strip()}')

# WRITE TO A FILE
print("\n=== WRITING TO A FILE ===")
with open('output.txt', 'w') as file:
    file.write('This is the first line. \n')
    file.write('This is the second one \n')
    file.write('\n')
    file.write('This is the third one \n')
print(f'Wrote to the file {file}')

with open('output.txt', 'r') as file:
    content = file.read()
    print(content)

print("=== APPENDING TO A FILE ===")
with open('output.txt', 'a') as file:
    file.write('This line was added later! \n')
with open('output.txt', 'r') as file:
    content = file.read()
    print(content)
