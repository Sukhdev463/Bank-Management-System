#user Registration Sign in or Sign up
from Database import *
import random
from bank import Bank
from Customer import *

def SignUp():
    username = input("Create Username: ")
    try:
        cursor.execute("SELECT Username FROM customers WHERE Username = %s;", (username,))
        temp = cursor.fetchone()  # Fetch the result of the query
        if temp:
            print("Username already exists")
            return  # Exit instead of recursively calling SignUp
        else:
            print("Username is available, please proceed")
            email = input("Enter your Email: ")
            password = input("Create Password: ")
            name = input("Enter your Name: ")
            age = input("Enter your Age: ")
            city = input("Enter your City: ")
            while True:
                account_number = int(random.randint(10000000, 99999999))  # Generate a random 8-digit account number
                cursor.execute("SELECT account_number FROM Customers WHERE account_number = %s;", (account_number,))
                temp = cursor.fetchone()  # Fetch the result of the query
                if temp:
                    continue
                else:
                    print("Your account number ",account_number)
                    break
            cobj = Customer(username, email, password, name, age, city, account_number)
            cobj.CreateUser()
            bobj = Bank(username, account_number)
            bobj.create_transaction_table()  # Creating transaction table for the user
    except sql.Error as e:
        print("Error during SignUp:", e)
             
def SignIn(username, password):
    try:
        cursor.execute("SELECT Password FROM Customers WHERE Username = %s;", (username,))
        temp = cursor.fetchone()  # Fetch the result of the query
        if not temp:
            print("Username not found.")
            return None
        if temp[0] == password:  # Compare the fetched password
            print("Sign In Successful")
            return username
        else:
            print("Invalid username or password.")
            return None
    except sql.Error as e:
        print("Error during SignIn:", e)
        return None
