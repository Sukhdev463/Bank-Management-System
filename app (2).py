from flask import Flask, render_template, request, redirect, session, url_for, flash
from Customer import *
from bank import *
from Register import SignIn, SignUp
from Database import cursor, mydb
import os

app = Flask(__name__)
# Generate a strong random key
app.secret_key = os.urandom(24).hex()  # This generates a new random key each time the app starts

@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        age = request.form['age']
        city = request.form['city']

        # Check for unique account number
        import random
        while True:
            account_number = random.randint(10000000, 99999999)
            cursor.execute("SELECT account_number FROM Customers WHERE account_number = %s;", (account_number,))
            if not cursor.fetchone():
                break

        c = Customer(username, email, password, name, age, city, account_number)
        c.CreateUser()

        b = Bank(username, account_number)
        b.create_transaction_table()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = SignIn(username, password)
        if user:
            session['username'] = username
            cursor.execute("SELECT account_number FROM customers WHERE Username = %s;", (username,))
            session['account_number'] = cursor.fetchone()[0]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    # Fetch user data for dashboard display
    cursor.execute("""
        SELECT Username, Email, Name, Age, City, balance, account_number, Status 
        FROM customers 
        WHERE Username = %s;
    """, (session['username'],))
    
    user_result = cursor.fetchone()
    
    # Create a dictionary to store user data
    user_data = {
        'username': user_result[0],
        'email': user_result[1],
        'name': user_result[2],
        'age': user_result[3],
        'city': user_result[4],
        'balance': user_result[5],
        'account_number': user_result[6],
        'status': user_result[7]
    }
    
    return render_template('dashboard.html', username=session['username'], user_data=user_data)


@app.route('/balance_enquiry')
def balance_enquiry():
    if 'username' not in session:
        return redirect('/login')
    
    try:
        b = Bank(session['username'], session['account_number'])
        cursor.execute("SELECT balance FROM customers WHERE username = %s;", (session['username'],))
        balance = cursor.fetchone()[0]
        return render_template('balance.html', balance=balance)
    except Exception as e:
        print(f"Error in balance_enquiry: {e}")
        return "Error loading balance page. Please try again."


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        amount = int(request.form['amount'])
        b = Bank(session['username'], session['account_number'])
        b.deposit(amount)
        return redirect('/dashboard')
    return render_template('transaction.html', action="Deposit")


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        amount = int(request.form['amount'])
        b = Bank(session['username'], session['account_number'])
        b.withdraw(amount)
        return redirect('/dashboard')
    return render_template('transaction.html', action="Withdraw")


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'username' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        receiver = int(request.form['receiver'])
        amount = int(request.form['amount'])
        b = Bank(session['username'], session['account_number'])
        b.fundtransfer(receiver, amount)
        return redirect('/dashboard')
    return render_template('transaction.html', action="Transfer")

@app.route('/pay_bill', methods=['GET', 'POST'])
def pay_bill():
    if 'username' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        bill_type = request.form.get('bill_type')
        amount_str = request.form.get('amount')
        
        # Validate input
        if not bill_type or bill_type not in Bank.SUPPORTED_BILLS:
            flash("Invalid or missing bill type.", "error")
            return render_template('pay_bill.html', bill_types=Bank.SUPPORTED_BILLS)
        
        try:
            amount = int(amount_str)
            if amount <= 0:
                flash("Amount must be a positive number.", "error")
                return render_template('pay_bill.html', bill_types=Bank.SUPPORTED_BILLS)
        except (ValueError, TypeError):
            flash("Invalid amount. Please enter a valid number.", "error")
            return render_template('pay_bill.html', bill_types=Bank.SUPPORTED_BILLS)
        
        # Process payment
        try:
            b = Bank(session['username'], session['account_number'])
            b.pay_bill(bill_type, amount)
            flash(f"Successfully paid ₹{amount} for {bill_type} bill.", "success")
            return redirect('/dashboard')
        except ValueError as e:
            # Handle expected errors like insufficient balance
            flash(f"Payment failed: {str(e)}", "error")
            return render_template('pay_bill.html', bill_types=Bank.SUPPORTED_BILLS)
        except Exception as e:
            # Handle unexpected errors
            print(f"ERROR in bill payment: {str(e)}")  # Log for debugging
            flash("An error occurred during bill payment. Please try again.", "error")
            return render_template('pay_bill.html', bill_types=Bank.SUPPORTED_BILLS)
    
    # GET request
    return render_template('pay_bill.html', bill_types=Bank.SUPPORTED_BILLS)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)