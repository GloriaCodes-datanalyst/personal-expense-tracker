import json
from datetime import datetime
from operator import index
from unittest import expectedFailure


# --- Transaction Class ---

class Transaction:
    def __init__(self, amount, description, category, date, transaction_type):
        self.amount = float(amount)         # The amount spent/earned (positive for income, negative for expense)
        self.description = description  # A description of the transaction (e.g., "Groceries")
        self.category = category       # Category of the transaction (e.g., "Food")

        if isinstance(date, str):
            try:
                self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")  # Date of the transaction (e.g., "2025-05-06")
            except ValueError:
                self.date = datetime.strptime(date, "%Y-%m-%d")
        else:
            self.date = date
            self.transaction_type = transaction_type   # This can be either income or expense

# --- Budget Manager Class ---

class BudgetManager:
    def __init__(self, filename="transaction.json"):
        self.filename = filename       # File to save transactions
        self.transactions = []         # List to store all Transaction objects
        self.load_transactions()       # Try to load existing transactions

    def add_transaction(self, amount, description, category, date, transaction_type):
        # Create a new Transaction object and add it to the list
        new_transaction = Transaction(amount, description, category, date, transaction_type)
        self.transactions.append(new_transaction)           # Adds a new transaction to the transactions list
        self.save_transactions()  # Save the updated transactions list to file

    def remove_transaction(self):
        desc = input("Enter the description of the transaction to be removed: ").strip().lower()

        for i, t in enumerate(self.transactions):
            if t.description.strip().lower() == desc:
                print(f"Removed: {t.date}: {t.description} | {t.amount} ")
                del self.transactions[i]
                self.save_transactions()
                return

        print("Transaction with that description not found")

    def get_balance(self):
        # Calculate total balance by summing up each transaction's amount
        income = sum(t.amount for t in self.transactions if t.transaction_type == "income")  # sums all the income from the user
        expense = sum(t.amount for t in self.transactions if t.transaction_type == "expense")  # sums all the expenses from the user
        return income - expense   # Adds up all amounts: positive and negative from all transactions  to get the balance

    def view_transactions(self):
        if not self.transactions:
            print("There is no transaction to display.")
            return
        print("All transactions.")    # Print all transactions in a readable format
        for t in self.transactions:
            try:
                print(f"{t.date.strftime('%Y-%m-%d')}: {t.description} | {t.amount:.2f} | {t.category} | {t.transaction_type}")
            except AttributeError:
                print(f"Invalid transaction entry skipped: {t}")

    def save_transactions(self):
        # Save transactions to a JSON file
        with open(self.filename, "w") as f:
            json.dump([
                {
                    "amount": t.amount,
                    "description": t.description,
                    "date": t.date.strftime("%Y-%m-%d"),   # This will convert the date into a string
                    "category": t.category,
                    "transaction_type": t.transaction_type
                }
                for t in self.transactions
            ], f, indent=4)

    def summarize_by_category(self):
        summary = {}   # Holds the totals by category

        for t in self.transactions:
            category = t.category.strip().lower()   # Make lowercases
            summary[category] = summary.get(category, 0) + t.amount


           # Printing the summary
            print("\n📊 Spending Summary by Category")
            for category, total in summary.items():
                print(f"{category.title()}: {total:.2f}")

    def summarize_by_month(self):
        summary = {}

        for t in self.transactions:
            try:
                month = t.date.strftime("%Y-%m") #e.g 2025-09
                if month not in summary:
                    summary[month] = {"income": 0, "expense": 0}
                if t.transaction_type == "income":
                    summary[month]["income"] += t.amount

                else:
                    summary[month]["expense"] += t.amount

            except AttributeError:   # If a transaction has an invalid date format, we skip it and print a warning.
                print(f"⚠️ Skipping transaction with invalid date: {t.date}")

        # Summary print
        print("\n📆 Summary by Month:")
        for month, total in sorted(summary.items()):
            print(f"{month} - Income: {total['income']:.2f} | Expense: {total['expense']:.2f}")

    def load_transactions(self):
        # Try to load transactions from the file
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                for item in data:

                    item["date"] = datetime.strptime(item["date"], "%Y-%m-%d")    # This will Convert date string to datetime object

                    transaction = Transaction(
                        item["amount"],
                        item["description"],
                        item["category"],
                        item["date"],
                        item.get("transaction_type", "expense")
                    )
                    self.transactions.append(transaction)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file does not exist or it's empty/corrupted, simply start with an empty list
            pass

# --- Menu and Main Logic ---

def display_menu():
    print("\nPersonal Expense Tracker")
    print("1. Add Transaction")
    print("2. View Transactions")
    print("3. Remove Transaction")
    print("4. View Balance")
    print("5. View spending by Category")
    print("6. Summary by Month")
    print("7. Exit")

def main():
    # Runs the whole program
    manager = BudgetManager()  # Create an instance of BudgetManager

    while True:
        display_menu()  # Show the menu to the user
        choice = input("Choose user option: ")  # Get the user's choice

        if choice == "1":  # Add Transaction
            # Get amount with error handling
            try:
                amount = float(input("Enter amount: "))      # Get's the amount and converts the number into a float
            except ValueError:          # If a user types a letter instead of a number they see an error and go back to the menu
                print("Please enter a valid number for the amount.")
                continue

            # Get the description and category
            description = input("Enter description: ")
            category = input("Enter category: ")

            # Get and validate date
            date_input = input("Enter date (YYYY-MM-DD): ")
            try:
                date = datetime.strptime(date_input, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD.")
                continue

            # Transaction Type (this must be at the same level as the try block)
            transaction_type = input("Is this an income or expense: ").strip().lower()
            if transaction_type not in ["income", "expense"]:
                print("Invalid transaction type. Enter 'income' or 'expense'.")
                continue

            manager.add_transaction(amount, description, category, date, transaction_type)
            print("Transaction added successfully")

        elif choice == "2":
            # View all transactions
            manager.view_transactions()

        elif choice == "3":
            manager.remove_transaction()

        elif choice == "4":
            # Display the current balance
            print(f"Total Balance: {manager.get_balance():.2f}")

        elif choice == "5":
            # Show spending summary by category
            manager.summarize_by_category()

        elif choice == "6":
           # Show summary by month
            manager.summarize_by_month()

        elif choice == "7":
            # Exit the program
            print("Auf Wiedersehen 😎")
            break

        else:
            print("Invalid option. Please choose 1–7.")

if __name__ == "__main__":
    main()


