# Write a Python script that creates a contact book (dictionary):
#Create a dictionary with at least 3 contacts, each with:
contacts = {
    'Ahmed Magdy': {'phone': '+201091140160', 'email': 'ahmed@test.com'},
    'Mostafa hussain': {'phone': '+201091140125', 'email': 'mostafa@test.com'},
    'Mohamed Shawkey': {'phone': '+201091140139', 'email': 'mohamed@test.com'}
}

# 3) Function: Add a new contact
def add_contact():
    name = str(input("Enter a name: ")).strip() .lower()
    phone = str(input("Enter a phone: "))
    email = str(input("Enter an email: ")).strip() .lower()
    if name in contacts:
        print(f"{name} is already exists! ")
    else:
        contacts[name] = {
            'phone': phone,
            'email': email
        }
        print(f"The name has been added successfully: {name}")

def display_contacts():
    for contact in contacts:
        print(contacts[contact])
    
def search_content():
    search = str(input("Enter a name: "))
    if search in contacts:
        print(f"Name is: {contacts[search]}")
    else:
        print("No name found!")