"""
Example banking transactions importer.

This importer simply generates random transactions for demonstration purposes.
"""

import random
import datetime

# chance, min_amount, max_amount, client, purpose
clients = [
    (1, 6000, 10000, 'Company XYZ', 'Salary'),  # Income
    (1, -1000, -2000, 'Landlord ABC', 'Rent'),  # Housing
    (0.2, -300, -1000, 'Hotel', 'Random purpose'),  # Travel
    (0.1, -20, -100, 'Gym', 'Random purpose'),  # Health
    (0.5, -50, -200, 'Supermarket', 'Random purpose'),  # Groceries
    (0.1, -50, -200, 'Insurance', 'Random purpose'),  # Insurance
    (0.1, -100, -1000, 'Furniture Store', 'Random purpose'),  # Home
    (0.1, -10, -100, 'Pharmacy', 'Random purpose'),  # Health
    (0.3, -20, -100, 'Restaurant', 'Random purpose'),  # Food
    (0.2, -10, -50, 'Transport Service', 'Random purpose'),  # Transport
    (0.1, -50, -200, 'Utilities Company', 'Random purpose'),  # Utilities
    (0.1, -30, -100, 'Internet Provider', 'Random purpose'),  # Utilities
    (0.1, -10, -50, 'Bookstore', 'Random purpose'),  # Books
    (0.2, -50, -200, 'Clothing Store', 'Random purpose'),  # Shopping
    (0.2, -100, -1000, 'Electronics Store', 'Random purpose'),  # Shopping
    (0.1, -20, -100, 'Entertainment Service', 'Random purpose'),  # Entertainment
    (0.1, -10, -100, 'Gift Shop', 'Random purpose'),  # Gifts
    (0.1, -10, -100, 'Charity Organization', 'Random purpose'),  # Donations
    (0.1, -100, -1000, 'Tax Office', 'Random purpose'),  # Taxes
    (0.1, -100, -1000, 'Travel Agency', 'Random purpose'),  # Travel
    (0.1, -10, -50, 'Subscription Service', 'Random purpose'),  # Subscriptions
    (0.1, -100, -500, 'Bank', 'Cash Withdrawal'),  # Bank
]

def fetch_transactions():
    random.seed(42)
    transactions = []
    # Needs fixed date to avoid duplicate transactions every time the script is run
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2030, 12, 31)
    current_date = start_date
    balance = random.randint(1000, 10000)
    while current_date <= end_date:
        for client in clients:
            chance, min_amount, max_amount, client_name, purpose = client
            amount = random.uniform(min_amount, max_amount)
            balance += amount
            if random.random() < chance:
                transactions.append({
                    'iban': 'DE12345678901234567890' if random.random() < 0.5 else 'DE09876543210987654321',
                    'internal': False,
                    'date': current_date,
                    'client': client_name,
                    'kind': 'Credit' if min_amount > 0 else 'Debit',
                    'purpose': purpose,
                    'amount': amount,
                    'balance': balance,
                    'currency': 'EUR',
                })
        # Move to the next month
        if current_date.month == 12:
            current_date = datetime.date(current_date.year + 1, 1, 1)
        else:
            current_date = datetime.date(current_date.year, current_date.month + 1, 1)
    return transactions