import os
import psycopg2


POSTGRES_CONF = {
    'dbname': os.getenv("POSTGRES_DB", "postgres"), 
    'user': os.getenv("POSTGRES_USER", "postgres"), 
    'password': os.getenv("POSTGRES_PASSWORD"), 
    'host': os.getenv("POSTGRES_HOST", "postgres"), 
    'port': os.getenv("POSTGRES_PORT", "5432"),
}

# The plugin will be used to fetch bank transactions and return them in a 
# format that can be processed by the syncer. The plugin should have a function
# called `fetch_transactions` that returns a list of transactions.
IMPORTER_PLUGIN = os.getenv("IMPORTER_PLUGIN", None)
if IMPORTER_PLUGIN is None:
    print("No importer plugin specified.")
    exit(1)
# Try to import the plugin.
try:
    importer = __import__(IMPORTER_PLUGIN, fromlist=['fetch_transactions'])
except ImportError:
    print(f"Failed to import plugin: {IMPORTER_PLUGIN}")
    exit(1)
print(f"Successfully imported plugin: {IMPORTER_PLUGIN}")

# The plugin will be used to classify the bank transactions. The plugin should
# have a function called `classify_transactions` that takes a list of transactions
# and returns a list of classified transactions.
CLASSIFIER_PLUGIN = os.getenv("CLASSIFIER_PLUGIN", None)
if CLASSIFIER_PLUGIN is None:
    print("No classifier plugin specified.")
    exit(1)
# Try to import the plugin.
try:
    classifier = __import__(CLASSIFIER_PLUGIN, fromlist=['classify_transactions'])
except ImportError:
    print(f"Failed to import plugin: {IMPORTER_PLUGIN}")
    exit(1)
print(f"Successfully imported plugin: {IMPORTER_PLUGIN}")

# Create tables if they don't exist.
with psycopg2.connect(**POSTGRES_CONF) as connection, connection.cursor() as cursor:
    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
        iban TEXT NOT NULL,
        internal BOOLEAN DEFAULT FALSE,
        date DATE NOT NULL,
        client TEXT NOT NULL,
        kind TEXT NOT NULL,
        purpose TEXT NOT NULL,
        amount DECIMAL NOT NULL,
        balance DECIMAL NOT NULL,
        currency TEXT NOT NULL,
        primary_class TEXT,
        secondary_class TEXT,
        PRIMARY KEY (iban, internal, date, client, kind, purpose, amount, balance, currency)
    )""")

# Insert transactions into the database.
with psycopg2.connect(**POSTGRES_CONF) as connection, connection.cursor() as cursor:
    for i, transaction in enumerate(importer.fetch_transactions()):
        primary_class, secondary_class = classifier.classify_transaction(transaction)
        cursor.execute("""
            INSERT INTO transactions (iban, internal, date, client, kind, purpose, amount, balance, currency, primary_class, secondary_class)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (iban, internal, date, client, kind, purpose, amount, balance, currency)
            DO NOTHING
        """, (
            transaction['iban'],
            transaction['internal'], # Whether the transaction is between our own accounts
            transaction['date'],
            transaction['client'],
            transaction['kind'],
            transaction['purpose'],
            transaction['amount'],
            transaction['balance'],
            transaction['currency'],
            primary_class or 'Not classified',
            secondary_class or 'Not classified',
        ))

print(f"Successfully inserted {i+1} transactions into the database.")
