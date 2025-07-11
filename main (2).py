from Register import *
from bank import *
from Database import cursor  # Ensure cursor is imported or initialized properly
import traceback

print("Welcome to my Banking Project")
user = None
account_number = None
status = False

while True:
    try:
        register = int(input("Enter 1 for Registering and 2 for Login: "))
        if register == 1:
            SignUp()
            print("Registration successful. Please login.")
        elif register == 2:
            username = input("Enter your Username: ")
            password = input("Enter your Password: ")
            user = SignIn(username, password)  # Pass username and password to SignIn
            if user:
                # Fetch account number after successful login
                cursor.execute("SELECT account_number FROM customers WHERE Username = %s;", (user,))
                acc = cursor.fetchone()
                if acc:
                    account_number = acc[0]  # Extract the single value from the tuple
                    status = True
                    break
                else:
                    print("Account not found for this user. Please register or try again.")
            else:
                print("Login failed. Please try again.")
        else:
            print("Invalid Input, please enter from the given options")
    except ValueError:
        print("Invalid Input, please enter a valid number")
    except Exception as e:
        print("An error occurred during registration/login:", e)
        traceback.print_exc()

if not status:
    print("Exiting program. Could not login.")
    exit()

bobj = Bank(user, account_number)  # Initialize Bank object once

while status:
    print(f"Welcome {user.capitalize()}! Choose the facility you want to avail.\n")
    try:
        facility = int(input("Enter 1. Balance Enquiry 2. Cash Deposit 3. Cash Withdrawal 4. Fund Transfer: "))
        if facility == 1:
            bobj.balanceenquiry()
        elif facility == 2:
            while True:
                try:
                    amount = int(input("Enter the amount to deposit: "))
                    bobj.deposit(amount)  # Commit handled inside the method
                    break
                except ValueError:
                    print("Enter a valid number.")
        elif facility == 3:
            while True:
                try:
                    amount = int(input("Enter the amount to withdraw: "))
                    bobj.withdraw(amount)  # Commit handled inside the method
                    break
                except ValueError:
                    print("Enter a valid number.")
        elif facility == 4:
            while True:
                try:
                    receive = int(input("Enter the receiver's account number: "))
                    amount = int(input("Enter the amount to transfer: "))
                    bobj.fundtransfer(receive, amount)  # Commit handled inside the method
                    break
                except ValueError:
                    print("Enter a valid number.")
        elif facility == 5:
            print(f"Available bill types: {', '.join(Bank.SUPPORTED_BILLS)}")
            bill_type = input("Enter the bill type: ")
            if bill_type not in Bank.SUPPORTED_BILLS:
                print("Invalid bill type.")
                continue
            try:
                amount = int(input("Enter the amount to pay: "))
                if amount <= 0:
                    print("Amount must be positive.")
                    continue
                bobj.pay_bill(bill_type, amount)
            except ValueError:
                print("Invalid amount. Please enter a number.")
        else:
            print("Invalid Input, please enter from the given options.")
    except ValueError:
        print("Invalid Input, please enter a valid number.")
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
