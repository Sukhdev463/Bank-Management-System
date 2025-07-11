#Customer Details
from Database import *
import mysql.connector as sql

class Customer:
    def __init__(self, username, email, password, name, age, city, account_number):
        self.__username = username
        self.__email = email
        self.__password = password
        self.__name = name
        self.__age = age
        self.__city = city
        self.__account_number = account_number
        
    def CreateUser(self):
        try:
            cursor.execute(
                "INSERT INTO Customers (Username, Email, Password, Name, Age, City, balance, account_number, Status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (self.__username, self.__email, self.__password, self.__name, self.__age, self.__city, 0, self.__account_number, 1)
            )
            mydb.commit()  # Commit changes to the database
            print("User created successfully!")
        except sql.IntegrityError:
            print("Error: Duplicate account number or username. Please try again.")
        except sql.Error as e:
            print("Error creating user:", e)