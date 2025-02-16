def classify_transaction(t):
    """
    Extend/modify this function to classify your transactions.
    """
    desc = t['description']
    if 'SALARY' in desc:
        return 'Income'
    if 'RENT' in desc:
        return 'Housing'
    if 'HOTEL' in desc:
        return 'Travel'
    if 'GYM' in desc:
        return 'Health'
    if 'SUPERMARKET' in desc:
        return 'Groceries'
    if 'INSURANCE' in desc:
        return 'Insurance'
    if 'FURNITURE' in desc:
        return 'Home'
    if 'PHARMACY' in desc:
        return 'Health'
    if 'RESTAURANT' in desc:
        return 'Food'
    if 'TRANSPORT' in desc:
        return 'Transport'
    if 'UTILITIES' in desc:
        return 'Utilities'
    if 'INTERNET' in desc:
        return 'Utilities'
    if 'BOOKSTORE' in desc:
        return 'Books'
    if 'CLOTHING' in desc:
        return 'Shopping'
    if 'ELECTRONICS' in desc:
        return 'Shopping'
    if 'ENTERTAINMENT' in desc:
        return 'Entertainment'
    if 'GIFT' in desc:
        return 'Gifts'
    if 'CHARITY' in desc:
        return 'Donations'
    if 'TAX' in desc:
        return 'Taxes'
    if 'TRAVEL' in desc:
        return 'Travel'
    if 'SUBSCRIPTION' in desc:
        return 'Subscriptions'
    if 'CASH WITHDRAWAL' in desc:
        return 'Bank'
    return 'Other'