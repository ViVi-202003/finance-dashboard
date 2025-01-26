"""
ING DE kontoauszug importer.
"""
import os
import glob
import pandas as pd
import PyPDF2
import datetime

def parse_kontoauszug_header(pdf_text):
    lines = pdf_text.split('\n')

    # Find line IBAN 0000 0000 0000 0000 0000 00
    for line in lines:
        if "IBAN" not in line:
            continue
        iban = "".join(line.split(' ')[1:])
        break
    else:
        raise ValueError("Invalid banking pdf header")

    # Find Alter Saldo 1.234,56 Euro and parse as float
    for line in lines:
        if "Alter Saldo" not in line:
            continue
        start_balance = float(line.split(' ')[2].replace('.', '').replace(',', '.'))
        break
    else:
        raise ValueError("Invalid banking pdf header")

    # Find Neuer Saldo 1.234,56 Euro and parse as float
    for line in lines:
        if "Neuer Saldo" not in line:
            continue
        end_balance = float(line.split(' ')[2].replace('.', '').replace(',', '.'))
        break
    else:
        raise ValueError("Invalid banking pdf header")

    return iban, start_balance, end_balance

def parse_kontoauszug_transactions(pdf_text):
    lines = pdf_text.split('\n')

    # Transactions are always in the format:
    # 01.01.1970 <kind (1 word)> <client (n words)> 1234.56,78
    # 01.01.1970 <purpose (n words)>
    # <next transaction>
    transactions = []
    line_idx = 0
    while line_idx < len(lines) - 1:
        l1, l2 = lines[line_idx], lines[line_idx + 1]
        line_idx += 1
        try:
            date = datetime.datetime.strptime(l1[:10], "%d.%m.%Y")
            # Note: date2 can be off date1!
            datetime.datetime.strptime(l2[:10], "%d.%m.%Y")
        except ValueError:
            continue
        try:
            amount = float(l1.split(' ')[-1].replace('.', '').replace(',', '.'))
        except ValueError:
            continue
        kind = l1[11:].split(' ')[0]
        client = " ".join(l1[11:].split(' ')[1:])
        purpose = l2[11:]
        transactions.append({
            "date": date,
            "kind": kind,
            "client": client,
            "purpose": purpose,
            "amount": amount
        })
        # Jump one row since this row is already processed
        line_idx += 1
    return transactions

def parse_kontoauszug_pdfs(pdfs):
    dfs = []
    for file in pdfs:
        print(f"Reading kontoauszug file {file}")
        # Open the PDF file
        reader = PyPDF2.PdfReader(file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
        iban, start_balance, end_balance = parse_kontoauszug_header(pdf_text)
        transactions = parse_kontoauszug_transactions(pdf_text)
        if not transactions:
            print("WARN No transactions found in PDF")
            continue
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        df['iban'] = iban
        # Sum up the amounts to get the balance. Sort by date first.
        df = df.sort_values('date')
        df['balance'] = start_balance + df['amount'].cumsum()
        # Check that the end balance is correct (.00 accuracy)
        if abs(end_balance - df['balance'].iloc[-1]) > 0.01:
            print(f"WARN End balance off by {end_balance - df['balance'].iloc[-1]}")
        # Convert back to string for database insertion
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df['currency'] = 'EUR'
        # If we have "Wertpapiergutschrift" or "Wertpapierkauf" in the purpose,
        # it's an internal transaction to/from the ING depot account.
        df['internal'] = df['kind'].str.contains("Wertpapiergutschrift|Wertpapierkauf")
        dfs.append(df)
    return pd.concat(dfs)

def parse_depot_transaction(pdf_text):
    lines = pdf_text.split('\n')

    # Look for Wertpapierbezeichnung
    for line in lines:
        if "Wertpapierbezeichnung" not in line:
            continue
        share_name = " ".join(line.split(' ')[1:])
        break
    else:
        raise ValueError("Invalid depot pdf transaction")

    # Look for Nominale Stück
    for line in lines:
        if "Nominale Stück" not in line:
            continue
        n_shares = float(line.split(' ')[-1].replace('.', '').replace(',', '.'))
        break
    else:
        raise ValueError("Invalid depot pdf transaction")

    # Look for Kurs
    for line in lines:
        if "Kurs " not in line:
            continue
        pershare = float(line.split(' ')[-1].replace('.', '').replace(',', '.'))
        break
    else:
        raise ValueError("Invalid depot pdf transaction")

    # Look for "Endbetrag zu Ihren Lasten" or "Endbetrag zu Ihren Gunsten"
    for line in lines:
        if "Endbetrag zu Ihren Lasten" in line or "Endbetrag zu Ihren Gunsten" in line:
            amount = float(line.split(' ')[-1].replace('.', '').replace(',', '.'))
            break
    else:
        raise ValueError("Invalid depot pdf transaction")

    # Look for Valuta
    for line in lines:
        if "Valuta" not in line:
            continue
        date = datetime.datetime.strptime(line.split(' ')[1], "%d.%m.%Y")
        break
    else:
        raise ValueError("Invalid depot pdf transaction")

    if "Endbetrag zu Ihren Gunsten" in pdf_text:
        amount *= -1
        n_shares *= -1
        kind = "Sell"
    else:
        kind = "Buy"
    return share_name, pershare, n_shares, amount, date, kind

def parse_depot_pdfs(pdfs):
    transactions = []
    for file in pdfs:
        print(f"Reading depot file {file}")
        # Open the PDF file
        reader = PyPDF2.PdfReader(file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
        with open(f"{file}.txt", "w") as f:
            f.write(pdf_text)
        share_name, pershare, n_shares, amount, date, kind = \
            parse_depot_transaction(pdf_text)
        transactions.append({
            # Handle the share as a separate account with the share name.
            "iban": share_name, # TODO: Refactor that the field is not called iban
            "date": date,
            "kind": kind,
            "purpose": f"{kind} {n_shares} {share_name}",
            "amount": amount,
            "n_shares": n_shares,
            "pershare": pershare
        })

    # Estimate the account balance over time. Since the shares change value
    # over time, we keep track of how many shares we bought/sold over time.
    dfs = []
    for share_name, df_share in pd.DataFrame(transactions).groupby('iban'):
        df_share = df_share.sort_values('date')
        n_shares = 0
        for i, transaction in df_share.iterrows():
            n_shares += transaction['n_shares']
            df_share.at[i, 'balance'] = n_shares * transaction['pershare']
        del df_share['n_shares']
        dfs.append(df_share)

    df = pd.concat(dfs)
    # Convert back to string for database insertion
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    df['currency'] = 'EUR'
    df['internal'] = True
    df['client'] = 'Depot'
    return df

def fetch_transactions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    print(f"Reading ING DE banking transactions from {input_dir}")

    pdfs = glob.glob(os.path.join(input_dir, "*.pdf"))
    kontoauszug_df = parse_kontoauszug_pdfs([f for f in pdfs if "Kontoauszug" in f])
    depot_df = parse_depot_pdfs([f for f in pdfs if "Depot" in f])

    all = pd.concat([kontoauszug_df, depot_df])
    all = all.sort_values('date')
    return all.to_dict(orient='records')

if __name__ == "__main__":
    print(fetch_transactions())