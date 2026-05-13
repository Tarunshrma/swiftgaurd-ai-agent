"""
Simple script to generate 100 SWIFT messages in proper format
"""

import os
import random
from datetime import datetime, timedelta

def generate_bic():
    """Generate a realistic BIC code"""
    bank_codes = ['CITI', 'JPMC', 'BARC', 'HSBC', 'DEUT', 'BNPP', 'SANT', 'UBSW', 'CSGN', 'RABO']
    countries = ['US', 'GB', 'DE', 'FR', 'CH', 'NL', 'ES', 'IT', 'JP', 'SG']
    
    bank = random.choice(bank_codes)
    country = random.choice(countries)
    location = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=2))
    branch = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
    
    return f"{bank}{country}{location}{branch}"

def generate_reference():
    """Generate transaction reference"""
    prefixes = ['PAY', 'TXN', 'REF', 'INV', 'FT']
    prefix = random.choice(prefixes)
    number = random.randint(100000, 999999)
    return f"{prefix}{number}"

def generate_amount():
    """Generate realistic transaction amount"""
    amounts = [
        round(random.uniform(100, 10000), 2),      # Small amounts
        round(random.uniform(10000, 100000), 2),   # Medium amounts  
        round(random.uniform(100000, 1000000), 2), # Large amounts
    ]
    return random.choice(amounts)

def generate_value_date():
    """Generate value date (YYMMDD format)"""
    base_date = datetime.now()
    days_forward = random.randint(0, 5)
    value_date = base_date + timedelta(days=days_forward)
    return value_date.strftime('%y%m%d')

def generate_customer_name():
    """Generate customer name"""
    first_names = ['JOHN', 'MARY', 'DAVID', 'SARAH', 'MICHAEL', 'EMMA', 'JAMES', 'ANNA']
    last_names = ['SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'GARCIA', 'MILLER', 'DAVIS']
    companies = ['TECH CORP LTD', 'GLOBAL INDUSTRIES INC', 'IMPORT EXPORT LLC', 'SERVICES COMPANY']
    
    if random.random() < 0.7:  # 70% individuals
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    else:  # 30% companies
        return random.choice(companies)

def generate_mt103_message(msg_id):
    """Generate MT103 Customer Credit Transfer"""
    reference = generate_reference()
    amount = generate_amount()
    currency = random.choice(['USD', 'EUR', 'GBP', 'JPY', 'CHF'])
    value_date = generate_value_date()
    sender_bic = generate_bic()
    receiver_bic = generate_bic()
    ordering_customer = generate_customer_name()
    beneficiary = generate_customer_name()
    
    # Ensure sender and receiver are different
    while receiver_bic == sender_bic:
        receiver_bic = generate_bic()
    
    # MT103 format
    swift_message = f"""{"{1:F01" + sender_bic + "0000000000}"}
{"{2:I103" + receiver_bic + "N}"}
{"{3:{{108:MT103}}}"}
{"{4:"}
:20:{reference}
:23B:CRED
:32A:{value_date}{currency}{amount:.2f}
:50K:/{random.randint(1000000000, 9999999999)}
{ordering_customer}
:59:/{random.randint(1000000000, 9999999999)}
{beneficiary}
:70:PAYMENT FOR SERVICES
:71A:OUR
-}}"""
    
    return swift_message

def generate_mt202_message(msg_id):
    """Generate MT202 General Financial Institution Transfer"""
    reference = generate_reference()
    amount = generate_amount()
    currency = random.choice(['USD', 'EUR', 'GBP', 'JPY', 'CHF'])
    value_date = generate_value_date()
    sender_bic = generate_bic()
    receiver_bic = generate_bic()
    
    # Ensure sender and receiver are different
    while receiver_bic == sender_bic:
        receiver_bic = generate_bic()
    
    # MT202 format
    swift_message = f"""{"{1:F01" + sender_bic + "0000000000}"}
{"{2:I202" + receiver_bic + "N}"}
{"{3:{{108:MT202}}}"}
{"{4:"}
:20:{reference}
:21:{reference}
:32A:{value_date}{currency}{amount:.2f}
:52A:{sender_bic}
:58A:{receiver_bic}
:72:/RETN/MSINV
-}}"""
    
    return swift_message

def main():
    """Generate 100 SWIFT messages and save them to files"""
    
    # Create directory for SWIFT messages
    messages_dir = "swift_messages"
    os.makedirs(messages_dir, exist_ok=True)
    
    print(f"Generating 100 SWIFT messages in directory: {messages_dir}")
    
    for i in range(1, 101):
        # Choose message type (70% MT103, 30% MT202)
        if random.random() < 0.7:
            message = generate_mt103_message(i)
            msg_type = "MT103"
        else:
            message = generate_mt202_message(i)
            msg_type = "MT202"
        
        # Save to file
        filename = f"{msg_type}_{i:03d}.swift"
        filepath = os.path.join(messages_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(message)
        
        if i % 10 == 0:
            print(f"Generated {i}/100 messages...")
    
    print(f"✅ Successfully generated 100 SWIFT messages in '{messages_dir}' directory")
    print(f"Files are named: MT103_001.swift, MT103_002.swift, MT202_001.swift, etc.")

if __name__ == "__main__":
    main()