import tkinter as tk
from tkinter import messagebox
from binance.client import Client
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
from datetime import datetime
import time




class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Profit Cloner")

        # Set up variables for login
        self.admin_username = "admin"
        self.admin_password = "admin123"

       

        # Set the window size
        self.root.geometry("800x600")

        # Set a dark theme color scheme
        self.bg_color = "#000"  # Background color
        self.fg_color = "#FFF"  # Foreground color (text color)
        self.button_bg = "#333"  # Button background color
        self.button_fg = "#FFF"  # Button text color

        # Set the background color of the root window
        self.root.config(bg=self.bg_color)

        # Create a frame for better organization
        self.login_frame = tk.Frame(root, bg=self.bg_color)
        self.login_frame.pack(padx=20, pady=20)

        # Create widgets with dark theme
        self.label_username = tk.Label(self.login_frame, text="Username:", font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color)
        self.label_password = tk.Label(self.login_frame, text="Password:", font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color)
        self.entry_username = tk.Entry(self.login_frame, font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)
        self.entry_password = tk.Entry(self.login_frame, show="*", font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)

        # Place widgets in the frame
        self.label_username.grid(row=0, column=0, pady=5, sticky=tk.E)
        self.label_password.grid(row=1, column=0, pady=5, sticky=tk.E)
        self.entry_username.grid(row=0, column=1, pady=5)
        self.entry_password.grid(row=1, column=1, pady=5)

        # Create login buttons
        self.admin_login_button = tk.Button(self.login_frame, text="Trader Login", command=self.admin_login, font=("Helvetica", 12),
                                           bg=self.button_bg, fg=self.button_fg)
        
        # Place login buttons in the frame
        self.admin_login_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Create a register client button
        self.register_client_button = tk.Button(self.login_frame, text="Register Client", command=self.open_add_client_window,
                                                font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        self.register_client_button.grid(row=4, column=0, columnspan=2, pady=10)


        # About Me button
        self.about_me_button = tk.Button(self.login_frame, text="About Me", command=self.show_about_me,
                                         font=("Helvetica", 12),
                                         bg=self.button_bg, fg=self.button_fg)
        self.about_me_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Initialize df as an empty DataFrame
        self.df = pd.DataFrame(columns=['symbol', 'price', 'qty', 'profit_loss'])
        try:
            # Create an SQLite database
            db_name = 'trading_app.db'
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()

            # Create a variable to store the connected clients
            self.connected_clients = set()

        
            # Create a new table to store admin-client mapping
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    api_key TEXT,
                    secret_key TEXT,
                    is_active INTEGER,
                    last_connection_time TEXT  -- Add the last_connection_time column

                    
                )
            ''')
            self.conn.commit()

        except sqlite3.Error as e:
            print(f"Error creating 'clients' table: {e}")


        
        

        self.connected_clients_listbox = None  # Added for the listbox to display connected clients

        

    def __del__(self):
        # Close the database connection when the application is closed
        self.conn.close()

    def admin_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username == self.admin_username and password == self.admin_password:
            self.open_api_key_secret_dialog()  # Prompt admin for API key and secret
        else:
            messagebox.showerror("Login Failed", "Invalid admin credentials")


    def open_api_key_secret_dialog(self):
        api_key_secret_window = tk.Toplevel(self.root)
        api_key_secret_window.title("Enter API Key and Secret")

        label_api_key = tk.Label(api_key_secret_window, text="API Key:", font=("Helvetica", 12))
        label_secret = tk.Label(api_key_secret_window, text="API Secret:", font=("Helvetica", 12))

        entry_api_key = tk.Entry(api_key_secret_window, font=("Helvetica", 12))
        entry_secret = tk.Entry(api_key_secret_window,  font=("Helvetica", 12))

        label_api_key.grid(row=0, column=0, pady=5, padx=10, sticky=tk.E)
        label_secret.grid(row=1, column=0, pady=5, padx=10, sticky=tk.E)

        entry_api_key.grid(row=0, column=1, pady=5, padx=10)
        entry_secret.grid(row=1, column=1, pady=5, padx=10)

        save_button = tk.Button(api_key_secret_window, text="Save", command=lambda: self.save_api_key_secret(
            entry_api_key.get(), entry_secret.get(), api_key_secret_window),
            font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def save_api_key_secret(self, api_key, secret_key, window):
            # Save the API key and secret, and update the Client instance
            if api_key and secret_key:
                self.binance_api_key = api_key
                self.binance_api_secret = secret_key
                self.client = Client(api_key=self.binance_api_key, api_secret=self.binance_api_secret)
                window.destroy()  # Close the API key and secret input window
                messagebox.showinfo("Success", "API Key and Secret updated successfully.")
                
                # Call admin_dash to move to the admin dashboard
                self.admin_dash()
            else:
                messagebox.showerror("Error", "API Key and Secret cannot be empty.")

    def admin_dash(self):
        # Hide the login frame
        self.login_frame.pack_forget()

        # Fetch admin's account information from Binance API
        account_info = self.fetch_account_info()

        # Create and display widgets for the admin dashboard with dark theme
        self.root.title("Trader Dashboard")
        self.root.geometry("800x600")

        # Create a frame for admin dashboard widgets
        admin_frame = tk.Frame(self.root, bg=self.bg_color)
        admin_frame.pack(pady=20)

        # Configure rows and columns to expand with window resizing
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Display "Trader Dashboard" at the top
        label_admin_welcome = tk.Label(admin_frame, text="Trader Dashboard", font=("Helvetica", 16), bg=self.bg_color,
                                    fg=self.fg_color)
        label_admin_welcome.grid(row=0, column=0, columnspan=3, pady=20)

        # Display connected clients
        self.display_connected_clients(admin_frame)

        # Display wallet information
        self.display_wallet_info(admin_frame, account_info)

        # Display recent trades summary
        self.display_recent_trades_summary(admin_frame)

        # Display total profit/loss
        self.display_total_profit_loss(admin_frame)

        # Add a settings button
        settings_button = tk.Button(admin_frame, text="Settings", command=self.open_settings_window,
                                    font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        settings_button.grid(row=0, column=1, pady=10, sticky=tk.E)


    def display_connected_clients(self, admin_frame):
        # Display client list on the right
        label_client_list = tk.Label(admin_frame, text="Client List", font=("Helvetica", 12), bg=self.bg_color,
                                    fg=self.fg_color)
        label_client_list.grid(row=1, column=2, pady=10, padx=10, sticky=tk.E)

        text_client_list = tk.Text(admin_frame, width=40, height=20, font=("Helvetica", 12), bg=self.bg_color,
                                fg=self.fg_color, state='disabled')
        text_client_list.grid(row=2, column=2, padx=10)

        # Fetch client information from the database
        clients = self.fetch_client_info()

        # Clear the text widget before inserting new data
        text_client_list.delete(1.0, tk.END)

        # Display client details in the text widget
        for client in clients:
            client_username = client['username']
            # Use get method to avoid KeyError
            text_client_list.insert(tk.END,
                                    f"Username: {client_username}\n")

        # Add a register client button at the bottom right
        register_client_button = tk.Button(admin_frame, text="Register Client", command=self.open_add_client_window,
                                        font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        register_client_button.grid(row=3, column=2, pady=10, sticky=tk.E)


    def display_wallet_info(self, admin_frame, account_info):
        # Display wallet list on the left
        label_wallet_list = tk.Label(admin_frame, text="Wallet List", font=("Helvetica", 12), bg=self.bg_color,
                                    fg=self.fg_color)
        label_wallet_list.grid(row=1, column=0, pady=10, padx=10, sticky=tk.W)

        text_wallet_list = tk.Text(admin_frame, width=40, height=20, font=("Helvetica", 12), bg=self.bg_color,
                                fg=self.fg_color)
        text_wallet_list.grid(row=2, column=0, padx=10)

        for asset in account_info:
            text_wallet_list.insert(tk.END,
                                    f"Token: {asset['asset']}, Free: {asset['free']}, Locked: {asset['locked']}\n")

    def display_recent_trades_summary(self, admin_frame):
        # Display recent trades as text
        label_recent_trades_summary = tk.Label(admin_frame, text="Recent Trades Summary", font=("Helvetica", 12),
                                            bg=self.bg_color, fg=self.fg_color)
        label_recent_trades_summary.grid(row=1, column=1, pady=10)

        text_recent_trades_summary = tk.Text(admin_frame, width=40, height=10, font=("Helvetica", 12), bg=self.bg_color,
                                            fg=self.fg_color)
        text_recent_trades_summary.grid(row=2, column=1)

        for _, trade in self.df.tail().iterrows():
            trade_type = 'Bought' if trade['profit_loss'] > 0 else 'Sold'
            self.update_recent_trades(trade_type, trade['symbol'], trade['qty'], trade['price'], text_recent_trades_summary)

    def display_total_profit_loss(self, admin_frame):
        # Display total profit/loss
        total_profit_loss = (self.df['price'].astype(float) * self.df['qty'].astype(float)).sum()
        label_total_profit_loss = tk.Label(admin_frame, text=f"Total Profit/Loss: {total_profit_loss}",
                                        font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color)
        label_total_profit_loss.grid(row=4, column=0, columnspan=3, pady=10)


    def save_new_keys(self, new_api_key, new_secret_key, settings_window):
        try:
            # Validate and save the new API and secret keys
            if new_api_key and new_secret_key:
                self.binance_api_key = new_api_key
                self.binance_api_secret = new_secret_key
                settings_window.destroy()  # Close the settings window
                messagebox.showinfo("Success", "API and secret keys updated successfully.")
            else:
                messagebox.showerror("Error", "New API and secret keys cannot be empty.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving new keys: {e}")

    def fetch_admin_trades(self):
        try:
            # Fetch admin's account information from Binance API
            account_info = self.fetch_account_info()

            all_trades = []

            # Fetch trades for each asset
            for asset in account_info:
                symbol = asset['asset']
                trades = self.client.get_my_trades(symbol=symbol)

                # Check if the asset has at least one trade
                if trades:
                    all_trades.extend(trades)

            # Process the trades if needed, e.g., store them in a database
            self.process_admin_trades(all_trades)

            return all_trades
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching trades: {e}")
            return []
    
    def open_settings_window(self):
        # Create a new Toplevel window for trader settings
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Trader Settings")

         # Create entry fields for new API and secret keys
        label_new_api_key = tk.Label(settings_window, text="New API Key:", font=("Helvetica", 12))
        label_new_secret_key = tk.Label(settings_window, text="New Secret Key:", font=("Helvetica", 12))

        label_new_api_key.grid(row=2, column=0, pady=5, padx=10, sticky=tk.E)
        label_new_secret_key.grid(row=3, column=0, pady=5, padx=10, sticky=tk.E)

        entry_new_api_key = tk.Entry(settings_window, font=("Helvetica", 12))
        entry_new_secret_key = tk.Entry(settings_window, font=("Helvetica", 12))

        entry_new_api_key.grid(row=2, column=1, pady=5, padx=10)
        entry_new_secret_key.grid(row=3, column=1, pady=5, padx=10)

         # Button to save the new keys
        save_button = tk.Button(settings_window, text="Save", command=lambda: self.save_new_keys(
            entry_new_api_key.get(), entry_new_secret_key.get(), settings_window),
            font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        save_button.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.E)

    def fetch_client_info(self):
        try:
            # Fetch all clients from the database
            self.cursor.execute('SELECT id, username, password, api_key, secret_key, is_active, IFNULL(last_connection_time, "") FROM clients')
            clients = self.cursor.fetchall()

            # Return the fetched clients as a list of dictionaries
            return [{'id': client[0], 'username': client[1], 'password': client[2], 'api_key': client[3],
                    'secret_key': client[4], 'is_active': client[5], 'last_connection_time': client[6]} for client in clients]
        except Exception as e:
            print(f"Error fetching client information: {e}")
            return []

    
    def process_admin_trades(self, trades):
        try:
            # Check if the database exists; if not, create it
            db_name = 'admintrade_app.db'
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()

            # Create a new table for admin trades if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    price REAL,
                    qty REAL,
                    time DATETIME
                )
            ''')

            # Process and store admin trades
            for trade in trades:
                symbol = trade['symbol']
                price = trade['price']
                qty = trade['qty']
                time = trade['time']

                # Store the trade details in your database table
                self.cursor.execute('''
                    INSERT INTO admin_trades (symbol, price, qty, time)
                    VALUES (?, ?, ?, ?)
                ''', (symbol, price, qty, time))

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error processing admin trades: {e}")
        finally:
            if self.conn:
                self.conn.close()



    def show_about_me(self):
        about_me_text = "I am Shivansh Saxena, the creator of this app, which is currently a work in progress. I welcome any feedback or inquiries .\n\n Feel free to reach out to me at shivanshs081@gmail.com"
        messagebox.showinfo("About Me", about_me_text)


    def fetch_account_info(self):
        try:
            if not self.binance_api_key or not self.binance_api_secret:
                # API keys are empty, prompt the user to enter them
                self.open_settings_window()
                return []  # Return an empty list for now, as the keys are not available
            else:
                # Fetch account information from Binance API
                account_info = self.client.get_account()
                balances = account_info['balances']
                # Filter out assets with zero balances
                non_zero_balances = [balance for balance in balances if float(balance['free']) + float(balance['locked']) > 0]
                return non_zero_balances
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching account information: {e}")
            return []


    def open_add_client_window(self):
        # Create a new Toplevel window for adding a client
        add_client_window = tk.Toplevel(self.root)
        add_client_window.title("Add Client")

        # Create labels and entry fields
        label_username = tk.Label(add_client_window, text="Username:", font=("Helvetica", 12))
        label_password = tk.Label(add_client_window, text="Password:", font=("Helvetica", 12))
        label_api_key = tk.Label(add_client_window, text="API Key:", font=("Helvetica", 12))
        label_secret_key = tk.Label(add_client_window, text="Secret Key:", font=("Helvetica", 12))

        entry_username = tk.Entry(add_client_window, font=("Helvetica", 12))
        entry_password = tk.Entry(add_client_window,  font=("Helvetica", 12))
        entry_api_key = tk.Entry(add_client_window, font=("Helvetica", 12))
        entry_secret_key = tk.Entry(add_client_window,  font=("Helvetica", 12))

        label_username.grid(row=0, column=0, pady=5, padx=10, sticky=tk.E)
        label_password.grid(row=1, column=0, pady=5, padx=10, sticky=tk.E)
        label_api_key.grid(row=2, column=0, pady=5, padx=10, sticky=tk.E)
        label_secret_key.grid(row=3, column=0, pady=5, padx=10, sticky=tk.E)

        entry_username.grid(row=0, column=1, pady=5, padx=10)
        entry_password.grid(row=1, column=1, pady=5, padx=10)
        entry_api_key.grid(row=2, column=1, pady=5, padx=10)
        entry_secret_key.grid(row=3, column=1, pady=5, padx=10)

        # Button to perform client registration
        register_button = tk.Button(add_client_window, text="Register", command=lambda: self.register_and_connect_client(
            entry_username.get(), entry_password.get(), entry_api_key.get(), entry_secret_key.get()),
            font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        register_button.grid(row=4, column=0, columnspan=2, pady=10)

    def open_register_client_window(self):
        # Create a new Toplevel window for registering a client
        register_client_window = tk.Toplevel(self.root)
        register_client_window.title("Register Client")

        # Create labels and entry fields
        label_client_username = tk.Label(register_client_window, text="Client Username:", font=("Helvetica", 12))
        entry_client_username = tk.Entry(register_client_window, font=("Helvetica", 12))

        label_client_username.grid(row=0, column=0, pady=5, padx=10, sticky=tk.E)
        entry_client_username.grid(row=0, column=1, pady=5, padx=10)

        # Button to perform client registration
        register_button = tk.Button(register_client_window, text="Register", command=lambda: self.register_and_connect_client(
            entry_client_username.get()),
            font=("Helvetica", 12), bg=self.button_bg, fg=self.button_fg)
        register_button.grid(row=1, column=0, columnspan=2, pady=10)



    def register_and_connect_client(self, client_username, password, api_key, secret_key):
        try:
            # Check if the client username already exists
            self.cursor.execute('SELECT * FROM clients WHERE username = ?', (client_username,))
            client = self.cursor.fetchone()

            if not client:
                # Insert the client data into the clients table
                self.cursor.execute(
                'INSERT INTO clients (username, password, api_key, secret_key, is_active, status, last_connection_time) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (client_username, password, api_key, secret_key, 1, 'Connected', datetime.now())
                )

                self.conn.commit()

                # Continue with the connection logic
                self.sync_admin_trades_with_clients(client_username, api_key, secret_key)

                # Update connected clients set
                self.connected_clients.add(client_username)

                # Call a method to update the GUI with the new client list
                self.update_connected_clients_widget()

                print(f"Client '{client_username}' registered and connected successfully.")
            else:
                # Update the client's status and last connection time
                self.cursor.execute('''
                    UPDATE clients SET is_active = 1, status = 'Connected',   WHERE username = ?
                ''', (datetime.now(), client_username))
                self.conn.commit()

                print(f"Client '{client_username}' reconnected successfully.")
        except Exception as e:
            print(f"Error registering and connecting client: {e}")

    def sync_admin_trades_with_clients(self):
        try:
            # Fetch the latest admin trades
            admin_trades = self.fetch_admin_trades()

            # Iterate through connected clients
            for client_username in self.connected_clients:
                client_data = self.connected_clients_data.get(client_username)
                if not client_data:
                    continue

                # Fetch client trades
                client_instance = client_data['client_instance']
                client_trades = client_instance.get_my_trades()

                # Check if there are new admin trades
                for admin_trade in admin_trades:
                    admin_trade_symbol = admin_trade['symbol']

                    # Check if the admin trade symbol exists in the client trades
                    if any(client_trade['symbol'] == admin_trade_symbol for client_trade in client_trades):
                        # Symbol exists, do nothing (trade already exists for the client)
                        pass
                    else:
                        # Symbol doesn't exist, copy admin trade to the client
                        self.copy_admin_trade_to_client(client_instance, admin_trade)

                messagebox.showinfo("Sync Successful", f"Client '{client_username}' synchronized with admin trades.")
        except Exception as e:
            messagebox.showerror("Sync Failed", f"Error synchronizing clients with admin trades: {e}")
  
    def copy_admin_trade_to_client(self, admin_api_key, admin_api_secret):
        # Fetch symbols for admin account
        admin_symbols = self.fetch_admin_symbols(admin_api_key, admin_api_secret)

        # Fetch client data from the database
        clients = self.fetch_client_info()

        for client in clients:
            client_api_key = client['api_key']
            client_api_secret = client['secret_key']

            # Fetch symbols for the client
            client_symbols = self.fetch_client_symbols(client_api_key, client_api_secret)

            # Find symbols that exist in both admin and client accounts
            common_symbols = set(admin_symbols).intersection(client_symbols)

            # Now you have the symbols that can be copied from admin to client
            for symbol in common_symbols:
                # Implement the trade copy logic here (e.g., creating buy/sell orders)
                self.copy_admin_trade(admin_api_key, admin_api_secret, client_api_key, client_api_secret, symbol)

    
    def copy_admin_trade(self, client_api_key, client_api_secret, admin_trade):
        try:
            # Create a client instance for the client using their API key and secret
            client = Client(api_key=client_api_key, api_secret=client_api_secret)

            symbol = admin_trade['symbol']
            price = admin_trade['price']
            qty = admin_trade['qty']

            # Determine the side based on the trade type (buy or sell)
            # You may need additional logic to determine the side based on admin trade information
            side = Client.SIDE_BUY if admin_trade['buy'] else Client.SIDE_SELL

            # Execute the trade for the client
            order = client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=qty,
                price=price
            )

            # Check if the order was successful
            if order['status'] == Client.ORDER_STATUS_FILLED:
                print(f"Trade for {qty} {symbol} at {price} executed successfully for client {client_api_key}.")
                return True
            else:
                print(f"Failed to execute trade for client {client_api_key}: {order['status']}")
                return False
        except Exception as e:
            print(f"Error copying trade for client {client_api_key}: {e}")

    def fetch_available_tokens(self):
        try:
            # Fetch all available tokens from Binance API
            exchange_info = self.client.get_exchange_info()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
            return symbols
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching available tokens: {e}")
            return []


    def view_admin_trades(self):
        # Fetch admin trades using admin's API
        admin_trades = self.fetch_admin_trades()

        # Create a new window to display admin trades
        admin_trades_window = tk.Toplevel(self.root)
        admin_trades_window.title("Admin Trades")

        # Create a text widget to display admin trades
        text_admin_trades = tk.Text(admin_trades_window, width=60, height=10, font=("Helvetica", 12), bg=self.bg_color, fg=self.fg_color)
        text_admin_trades.pack()

        # Display admin trades in the text widget
        for trade in admin_trades:
            text_admin_trades.insert(tk.END, f"Symbol: {trade['symbol']}, Price: {trade['price']}, Quantity: {trade['qty']}\n")
    
            return False

    def check_sufficient_funds(self, client_info, total_admin_value):
        try:
            # Assuming USDT is the base currency for funds comparison
            client_usdt_balance = next(asset['free'] for asset in client_info if asset['asset'] == 'USDT')
            
            # Convert the client's USDT balance to a float
            client_usdt_balance = float(client_usdt_balance)

            # Check if the client has enough funds to copy admin trades
            if client_usdt_balance >= total_admin_value:
                return True
            else:
                # Calculate the required additional funds
                required_funds = total_admin_value - client_usdt_balance
                messagebox.showerror("Insufficient Funds", f"Client needs ${required_funds:.2f} more to copy admin trades.")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Error checking client funds: {e}")
            return False

    def fetch_client_symbols(self, client_api_key, client_api_secret):
        # Initialize the client using the client's API key and secret
        client = Client(api_key=client_api_key, api_secret=client_api_secret)

        # Fetch the client's account information
        client_account_info = client.get_account()

        # Extract and return a list of symbols the client is trading
        client_symbols = [balance['asset'] for balance in client_account_info['balances']]

        return client_symbols

    def fetch_admin_symbols(self):
        try:
            # Fetch admin's account information using their API key and secret
            admin_account_info = self.client.get_account()

            # Extract and return a list of symbols that the admin is trading
            admin_symbols = [balance['asset'] for balance in admin_account_info['balances']]

            return admin_symbols
        except Exception as e:
            print(f"Error fetching admin symbols: {e}")
            return []


    def execute_buy_order(self, symbol, price, qty):
        try:
            # Use the client's API to place a buy order
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=qty,
                price=price
            )
            # Check if the order was successful
            if order['status'] == Client.ORDER_STATUS_FILLED:
                messagebox.showinfo("Order Executed", f"Buy order for {qty} {symbol} at {price} executed successfully.")
            else:
                messagebox.showerror("Order Failed", f"Failed to execute buy order: {order['status']}")
        except Exception as e:
            messagebox.showerror("Error", f"Error executing buy order: {e}")



if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()

   