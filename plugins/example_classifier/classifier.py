def classify_transaction(t):
    """
    Extend/modify this function to classify your transactions.
    """
    if 'SALARY' in t['purpose'].upper():
        return 'Income', 'Salary'
    if 'RENT' in t['purpose'].upper():
        return 'Housing', 'Rent'
    
    if 'HOTEL' in t['client'].upper():
        return 'Travel', 'Hotel'
    if 'GYM' in t['client'].upper():
        return 'Health', 'Gym'
    if 'SUPERMARKET' in t['client'].upper():
        return 'Groceries', 'Supermarket'
    if 'INSURANCE' in t['client'].upper():
        return 'Insurance', 'Insurance'
    if 'FURNITURE' in t['client'].upper():
        return 'Home', 'Furniture'
    if 'PHARMACY' in t['client'].upper():
        return 'Health', 'Pharmacy'
    if 'RESTAURANT' in t['client'].upper():
        return 'Food', 'Restaurant'
    if 'TRANSPORT' in t['client'].upper():
        return 'Transport', 'Transport'
    if 'UTILITIES' in t['client'].upper():
        return 'Utilities', 'Utilities'
    if 'INTERNET' in t['client'].upper():
        return 'Utilities', 'Internet'
    if 'BOOKSTORE' in t['client'].upper():
        return 'Books', 'Bookstore'
    if 'CLOTHING' in t['client'].upper():
        return 'Shopping', 'Clothing'
    if 'ELECTRONICS' in t['client'].upper():
        return 'Shopping', 'Electronics'
    if 'ENTERTAINMENT' in t['client'].upper():
        return 'Entertainment', 'Entertainment'
    if 'GIFT' in t['client'].upper():
        return 'Gifts', 'Gift'
    if 'CHARITY' in t['client'].upper():
        return 'Donations', 'Charity'
    if 'TAX' in t['client'].upper():
        return 'Taxes', 'Tax'
    if 'TRAVEL' in t['client'].upper():
        return 'Travel', 'Travel'
    if 'SUBSCRIPTION' in t['client'].upper():
        return 'Subscriptions', 'Subscription'
    if 'CASH WITHDRAWAL' in t['purpose'].upper():
        return 'Bank', 'Cash Withdrawal'
    return 'Other', 'Other'