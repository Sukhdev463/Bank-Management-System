#Bank Services
from Database import *
import datetime
class Bank:
    SUPPORTED_BILLS = ['electricity', 'water', 'cable', 'internet', 'phone']
    
    def __init__(self, username, account_number):
        self.username = username
        self.account_number = account_number
        
        
    def create_transaction_table(self):
        # Sanitize the table name to prevent SQL injection
        table_name = f"{self.username}_transactions".replace(" ", "_").replace(";", "").replace("--", "")
        #print(f"Creating table: {table_name}")  # Debugging statement
        
        # Create a table for transactions
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS `{table_name}` ("
            "timedate VARCHAR(30), "
            "account_number INTEGER, "
            "remarks VARCHAR(30), "
            "amount INTEGER)"
        )
        mydb.commit()
        print(f"Table {table_name} created successfully.")  # Debugging statement

    def balanceenquiry(self):  # Check the balance of the account
        try:
            cursor.execute("SELECT balance FROM customers WHERE username = %s;", (self.username,))
            temp = cursor.fetchone()
            print(f"{self.username}'s balance is {temp[0]}")
        except sql.Error as e:
            print("Error during balance enquiry:", e)
        
        
    def deposit(self, amount):  # Deposit money into the account
        try:
            cursor.execute("SELECT balance FROM customers WHERE username = %s;", (self.username,))
            temp = cursor.fetchone()
            new_balance = temp[0] + amount
            cursor.execute("UPDATE customers SET balance = %s WHERE username = %s;", (new_balance, self.username))
            self.balanceenquiry()
            cursor.execute(
                f"INSERT INTO {self.username}_transactions (timedate, account_number, remarks, amount) "
                "VALUES (%s, %s, %s, %s);",
                (datetime.datetime.now(), self.account_number, "Deposit", amount)
            )
            mydb.commit()
            print(f"{self.username}, {amount} has been successfully deposited into your account.")
        except sql.Error as e:
            print("Error during deposit:", e)


    def withdraw(self, amount):  # Withdraw money from the account
        try:
            cursor.execute("SELECT balance FROM customers WHERE username = %s;", (self.username,))
            temp = cursor.fetchone()
            if amount > temp[0]:
                print("Insufficient balance.")
            else:
                new_balance = temp[0] - amount
                cursor.execute("UPDATE customers SET balance = %s WHERE username = %s;", (new_balance, self.username))
                self.balanceenquiry()
                cursor.execute(
                    f"INSERT INTO {self.username}_transactions (timedate, account_number, remarks, amount) "
                    "VALUES (%s, %s, %s, %s);",
                    (datetime.datetime.now(), self.account_number, "Withdrawal", amount)
                )
                mydb.commit()
                print(f"{self.username}, {amount} has been successfully withdrawn from your account.")
        except sql.Error as e:
            print("Error during withdrawal:", e)


    def fundtransfer(self, receive, amount):  # Transfer money to another account
        try:
            cursor.execute("SELECT balance FROM customers WHERE username = %s;", (self.username,))
            sender_balance = cursor.fetchone()[0]
            if amount > sender_balance:
                print("Insufficient balance.")
                return
            cursor.execute("SELECT balance FROM customers WHERE account_number = %s;", (receive,))
            receiver = cursor.fetchone()
            if not receiver:
                print("Receiver's account does not exist.")
                return
            receiver_balance = receiver[0]
            new_sender_balance = sender_balance - amount
            new_receiver_balance = receiver_balance + amount
            cursor.execute("UPDATE customers SET balance = %s WHERE username = %s;", (new_sender_balance, self.username))
            cursor.execute("UPDATE customers SET balance = %s WHERE account_number = %s;", (new_receiver_balance, receive))
            cursor.execute("SELECT username FROM customers WHERE account_number = %s;", (receive,))
            receiver_username = cursor.fetchone()
            self.balanceenquiry()
            cursor.execute(
                "INSERT INTO {}_transactions (timedate, account_number, remarks, amount) "
                "VALUES (%s, %s, %s, %s);".format(receiver_username[0]),
                (datetime.datetime.now(), self.account_number, f"Fund Transfer from {self.account_number}", amount)
            )
            cursor.execute(
                "INSERT INTO {}_transactions (timedate, account_number, remarks, amount) "
                "VALUES (%s, %s, %s, %s);".format(self.username),
                (datetime.datetime.now(), self.account_number, f"Fund Transfer -> {receive}", amount)
            )
            mydb.commit()
            print(f"{self.username}, {amount} has been successfully transferred to account {receive}.")
        except sql.Error as e:
            print("Error during fund transfer:", e)
            
    def pay_bill(self, bill_type, amount):
        """
        Pay a bill of specified type and amount.
        
        Args:
            bill_type (str): Type of bill to pay (must be in SUPPORTED_BILLS)
            amount (int): Amount to pay (must be positive)
            
        Returns:
            bool: True if payment successful, False otherwise
        """
        if bill_type not in self.SUPPORTED_BILLS:
            raise ValueError(f"Unsupported bill type: {bill_type}")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        try:
            # Check balance
            cursor.execute("SELECT balance FROM customers WHERE username = %s;", (self.username,))
            temp = cursor.fetchone()
            if not temp:
                raise Exception(f"Account not found for username: {self.username}")
                
            current_balance = temp[0]
            if amount > current_balance:
                raise ValueError(f"Insufficient balance. Available: {current_balance}, Required: {amount}")
            
            # Update balance
            new_balance = current_balance - amount
            cursor.execute("UPDATE customers SET balance = %s WHERE username = %s;", 
                          (new_balance, self.username))
            
            # Record transaction
            # Ensure table name is properly formatted for SQL
            table_name = f"{self.username}_transactions".replace(" ", "_").replace(";", "").replace("--", "")
            remarks = f"Paid {bill_type} Bill"
            
            # Insert transaction record
            cursor.execute(
                f"INSERT INTO `{table_name}` (timedate, account_number, remarks, amount) "
                "VALUES (%s, %s, %s, %s);",
                (datetime.datetime.now(), self.account_number, remarks, amount)
            )
            
            # Commit transaction
            mydb.commit()
            return True
            
        except Exception as e:
            # Rollback on error
            if mydb.is_connected():
                mydb.rollback()
            raise e  # Re-raise the exception for higher-level handling