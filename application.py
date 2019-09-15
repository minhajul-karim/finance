import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from dateutil import tz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from helpers import apology, login_required, lookup, usd

database_file = "postgres://faoqgogsskzcek:795a7c81e2e6c3cdc7634e7e71a2c39acc0238ceae5efa9644c76ab0b257f97c@ec2-174-129-227-146.compute-1.amazonaws.com:5432/ddf9frqo66ole3"

# Configure application
app = Flask(__name__)
app.secret_key = "�#�-ާg'���3RCw"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

engine = db.engine
connection = engine.connect()

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Query to select all data from users table
    query = text("SELECT * FROM transactions WHERE userid = :userid ORDER BY symbol") 

    # Fetch all rows obtained from the above query
    rows = (connection.execute(query, userid=session["user_id"])).fetchall()
    grand_total = 0

    # Declare an empty list
    row_list = []

    # Travarse all rows for logged in user
    if rows:
        
        # Convert Resultproxy objetcs into list of dictionaries
        for row in rows:
            row_list.append(dict(row))

        # Add additional information to row_list
        for row in row_list:
            
            # Get information for symbol
            info = lookup(row["symbol"])

            # If information is received
            if info:

                # Total value of each holding
                per_stock_total = row["shares"] * info["price"]

                # Calculate total spent money
                grand_total += per_stock_total

                # Insert required indices into row to display in template
                row["name"] = info["name"]
                row["price"] = info["price"]
                row["total"] = per_stock_total

    # Check user's available balance
    query = text("SELECT cash FROM users WHERE id = :id")
    result = (connection.execute(query, id=session["user_id"])).fetchall()
    current_cash = result[0]["cash"]
    grand_total += current_cash

    # Render index template
    return render_template("index.html", rows=row_list, current_cash=current_cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # When user submits form
    if request.method == "POST":

        # Check for empty symbol
        if request.form.get("symbol") == "":
            return apology("missing symbol", 400)

        # Check for empty shares
        elif request.form.get("shares") == "":
            return apology("missing shares", 400)

        # Check if shares are negative
        elif request.form.get("shares")[0] == "-":
            return apology("Shares must not negative", 400)

        # Check if shares are float
        elif not request.form.get("shares").replace(".", "", 1).isdigit():
            return apology("Shares must not be fractional", 400)

        # Check if shares are non-numeric
        elif not request.form.get("shares").isdigit():
            return apology("Shares must be numeric", 400)

        # Get data for given symbol
        info = lookup(request.form.get("symbol"))

        # Data available
        if info:

            # Calculate new cost
            new_cost = int(request.form.get("shares"))*float(info["price"])

            # Check user's available balance
            query = text("SELECT cash FROM users WHERE id = :id")
            result = (connection.execute(query, id=session["user_id"])).fetchall()
            current_balance = result[0]["cash"]

            # Check user's affordability
            if new_cost > current_balance:
                return apology("Not enough cash", 400)

            # Check if user has purchased same stock before
            query = text("SELECT * FROM transactions WHERE userid = :userid AND symbol = :symbol")
            symbol_row = (connection.execute(query, userid=session["user_id"], symbol=info["symbol"])).fetchall()

            # Update shares if user has already purchased a stock before
            if symbol_row:

                # Get the current number of shares
                current_shares = symbol_row[0]["shares"]

                # Calculate updated shares
                updated_shares = current_shares + int(request.form.get("shares"))

                # Update transactions table
                query = text("UPDATE transactions SET shares = :shares WHERE userid = :userid AND symbol = :symbol")
                connection.execute(query, shares=updated_shares, userid=session["user_id"], symbol=info["symbol"])

                # Calculate new cash
                updated_cash = current_balance - new_cost

                # Update users table
                query = text("UPDATE users SET cash = :cash WHERE id = :id")
                connection.execute(query, shares=updated_shares, cash=updated_cash, id=session["user_id"])

            # Insert data into transactions table
            else:

                # Insert transactions table
                query = text("INSERT INTO transactions (userid, symbol, shares) VALUES (:userid, :symbol, :shares)")
                connection.execute(query, userid=session["user_id"], symbol=info["symbol"], shares=request.form.get("shares"))
                
                # Calculate post purchase balance
                updated_cash = current_balance - new_cost

                # Update cash of users table
                query = text("UPDATE users SET cash = :cash WHERE id = :id")
                connection.execute(query, userid=session["user_id"], cash=updated_cash, id=session["user_id"])

            # Get transaction time
            current_time = (datetime.utcnow()).replace(microsecond=0)

            # Update history table
            query = text("INSERT INTO history (userid, symbol, shares, price, date_time) VALUES (:userid, :symbol, :shares, :price, :date_time)")
            connection.execute(query, userid=session["user_id"], symbol=info["symbol"], shares=request.form.get("shares"), price=info["price"], date_time=current_time)

        # Notify user for invalid symbol
        else:
            return apology("invalid symbol", 400)

        # Send the flash message to homepage
        flash("Congrats! You've successfully bought!")

        # Redirect to homepage
        return redirect(url_for("index"))

    # If user clicks the buy button
    return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    if len(request.args.get("username")) >= 1:

        # Query db for username
        query = text("SELECT id FROM users where username = :username LIMIT 1") 
        user_row = connection.execute(query, username=request.args.get("username")).fetchall()

        # If username exists
        if user_row:
            return jsonify(False)

        # username doesn't exist
        else:
            return jsonify(True)
    else:
        apology("Username must contain at least one character", 403)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Fetch data form db
    query = text("SELECT * FROM history WHERE userid = :userid ORDER BY date_time DESC") 
    rows = (connection.execute(query, userid=session["user_id"])).fetchall()

    # Get local time zone from frontend
    local_zone = request.args.get("zone")
    return local_zone
    # local_zone = "Asia/Dhaka"
    
    # source https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
    # from_zone = tz.gettz("UTC")
    # to_zone = tz.gettz(local_zone)

    # # Declare an empty list
    # row_list = []

    # # If hisoty exists
    # if rows:

    #     # Convert Resultproxy objetcs into list of dictionaries
    #     for row in rows:
    #         row_list.append(dict(row))
        
    #     # Travarse all rows for logged in user
    #     for row in row_list:
            
    #         # Get information for symbol
    #         info = lookup(row["symbol"])

    #         # Insert required indices into row to display in template
    #         row["price"] = info["price"]

    #         # Get the date_time column
    #         utc = row["date_time"]

    #         # Tell the datetime object that it's in UTC
    #         utc = utc.replace(tzinfo=from_zone)

    #         # Convert to local time
    #         local_time = utc.astimezone(to_zone)

    #         # Format local time
    #         formatted_local_time = local_time.strftime("%d-%m-%Y %I:%M:%S %p")
    #         print(formatted_local_time)
    #         print(type(formatted_local_time))

    #         # Insert into row_list
    #         row["transaction_time"] = formatted_local_time

    # return render_template("history.html", rows=row_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query to select all data from users table
        query = text("SELECT * FROM users WHERE username = :username") 

        # Fetch the row obtained from the above query
        result = (connection.execute(query, username=request.form.get('username'))).fetchone()

        # Ensure username exists and password is correct
        if not result or not check_password_hash(result[2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = result[0]

        # Save username to the sesssion
        session["username"] = request.form.get("username")

        # Send the flash message to homepage
        flash("Welcome!")

        # Redirect user to home page
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote"""

    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Check for empty symbol
        if symbol == "":
            return apology("missing symbol", 400)

        # Get information for given symbol
        info = lookup(symbol)

        # Show information
        if info:
            return render_template('quote.html', info=info)

        # Notify for invalid symbol
        else:
            return apology("invalid symbol", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Clear any previous session
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # Ensure is username is more than 3 characters
        if not len(request.form.get("username")) >= 1:
            return apology("username must be of at least one character!", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 400)

         # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Must provide password again", 400)

        # Check both passwords
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords mismatched!", 400)

        # Check if username alrady exists
        query = text("SELECT id FROM users where username = :username LIMIT 1") 
        result = (connection.execute(query, username=request.form.get('username'))).fetchone()

        # If users exists
        if result:
            return apology("Username not available!", 400)

        # Query to insert data into database
        query = text("INSERT INTO users (username, hash) VALUES (:username, :hash) RETURNING id")

        # Receive the correspondig id
        rows = (connection.execute(query, username=request.form.get('username'), hash=generate_password_hash(request.form.get('password')))).fetchall()
        
        # connection.close()

        # Save user id to the sesssion
        session["user_id"] = rows[0]["id"]
        
        # Save username to the sesssion
        session["username"] = request.form.get("username")

        # Send the flash message to homepage
        flash("Congrats!")

        # Redirect user to home page
        return redirect(url_for("index"))


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Grab form data if user submits the form
    if request.method == "POST":
        
        # Check for empty stock
        if not request.form.get("symbol"):
            return apology("Must provide symbol", 400)

        # Check for empty shares
        elif not request.form.get("shares"):
            return apology("Must provide number of shares", 400)

        # Number of shares of a stock
        query = text("SELECT shares FROM transactions WHERE userid = :userid AND symbol = :symbol") 
        result = (connection.execute(query, userid=session["user_id"], symbol=request.form.get("symbol"))).fetchall()

        # Restrict user from selling more shares than s/he has
        if int(request.form.get("shares")) > result[0]["shares"]:
            return apology("Don't have enough shares", 400)

        # Get information about this stock
        info = lookup(request.form.get("symbol"))

        # Current selling price
        selling_price = info["price"] * int(request.form.get("shares"))

        # Update the cash in users table
        query = text("SELECT cash FROM users WHERE id = :id") 
        cash_row = (connection.execute(query, id=session["user_id"])).fetchall()

        # Update cash in users table
        updated_cash = cash_row[0]["cash"] + selling_price
        query = text("UPDATE users SET cash = :cash WHERE id = :id")
        connection.execute(query, cash=updated_cash, id=session["user_id"])

        # DELETE row if user wills to sell all of his shares of a stock
        if (int(request.form.get("shares")) == result[0]["shares"]):
            query = text("DELETE FROM transactions WHERE userid = :userid AND symbol = :symbol")
            connection.execute(query, userid=session["user_id"], symbol=request.form.get("symbol"))

        # Update number of shares in transaction table
        else:
            updated_share = result[0]["shares"] - int(request.form.get("shares"))
            query = text("UPDATE transactions SET shares = :shares WHERE userid = :userid AND symbol = :symbol")
            connection.execute(query, shares=updated_share, userid=session["user_id"], symbol=request.form.get("symbol"))

        # Get transaction time
        current_time = (datetime.utcnow()).replace(microsecond=0)
        sold_shares = int(request.form.get("shares")) * -1

        # Update history table
        query = text("INSERT INTO history (userid, symbol, shares, price, date_time) VALUES (:userid, :symbol, :shares, :price, :date_time)")
        connection.execute(query, userid=session["user_id"], symbol=request.form.get("symbol"), shares=sold_shares, price=info["price"], date_time=current_time)

        # Send the flash message to homepage
        flash("Congrats! You've successfully sold!")

        # Return to homepage
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        query = text("SELECT symbol FROM transactions WHERE userid = :userid GROUP BY symbol") 
        symbol_rows = (connection.execute(query, userid=session["user_id"])).fetchall()
        return render_template("sell.html", symbol_rows=symbol_rows)


@app.route("/save_symbol_in_session", methods=["GET"])
def save_symbol_in_session():
    """ Save the symbol into session """

    # Grab the symbol form a row
    symbol = request.args.get("sym")

    # Return true if the symbol is received successfully, else return false
    if symbol:
        session["symbol"] = symbol
        return jsonify(True)
    else:
        return jsonify(False)

@app.route("/buythis", methods=["GET"])
def buythis():
    """Buy shares of specific stock"""

    return render_template("buy_this.html", symbol=session["symbol"])

@app.route("/sellthis", methods=["GET"])
def sellthis():
    """Sell shares of specific stock"""

    return render_template("sell_this.html", symbol=session["symbol"])


def errorhandler(e):
    """Handle error"""

    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
