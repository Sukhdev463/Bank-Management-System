#Database Managment Banking
import mysql.connector as sql
mydb=sql.connect( #connecting to the database localhost
    host="localhost", 
    user="root",
    passwd="srijan",
    database="bank"       
)

cursor = mydb.cursor()#creating a cursor object for further use in program

def db_query(str): #function takes query as a input and executes it
    if not mydb.is_connected():# Check if the connection is active
            mydb.reconnect(attempts=3, delay=5)# Reconnect if the connection is lost
    cursor.execute(str) #executing the query
    result = cursor.fetchall() #fetching the result of the query
    return result

def CreateCustomerTable():#function to create a table Customers
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS customers( #creating a table Customers
     Username varchar(20) NOT NULL,
     Email varchar(20) NOT NULL,
     Password varchar(20) NOT NULL,
     Name varchar(20) NOT NULL,
     Age integer NOT NULL,
     City varchar(20) NOT NULL,
     balance integer NOT NULL,
     account_number integer NOT NULL,
     Status Boolean NOT NULL )
 ''')

mydb.commit()#commiting the changes to the database i.e. saving the changes or checkpointing the changes
if __name__ == "__main__":
    CreateCustomerTable()#calling the function to create a table Customers onl if the file is run as main file