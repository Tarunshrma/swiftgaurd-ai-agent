# SWIFT Overview

## Introduction
The **Society for Worldwide Interbank Financial Telecommunication (SWIFT)** is a global messaging network used by financial institutions to securely exchange information and instructions. 

SWIFT itself does not hold or transfer funds; instead, it provides a standardized and secure platform to transmit financial messages such as payment orders, securities transactions, and trade confirmations.

---

## Key Features
- **Global Network**: Connects over 11,000 institutions in more than 200 countries.
- **Standardization**: Provides ISO-standard message formats (e.g., MT and MX messages).
- **Security**: Ensures confidentiality, integrity, and authentication of messages.
- **Reliability**: Operates with near-continuous availability and resilience.
- **Compliance Tools**: Supports AML (Anti-Money Laundering), KYC (Know Your Customer), and sanctions screening.

---

## Message Types
SWIFT messages are structured and categorized into types, known as **MT (Message Type)** or **MX (XML-based)** formats.

### Common MT Messages
- **MT103**: Single Customer Credit Transfer (used for cross-border payments).
- **MT202**: General Financial Institution Transfer (bank-to-bank settlements).
- **MT940**: Customer Statement Message.
- **MT950**: Statement Message.

### MX Messages
- Based on the ISO 20022 XML standard.
- Designed for richer data structures and modern interoperability.

---

## SWIFT Codes (BIC)
Every SWIFT participant has a unique **Bank Identifier Code (BIC)**, often called a **SWIFT Code**.  
Format: `AAAA BB CC DDD`
- `AAAA` – Bank code  
- `BB` – Country code  
- `CC` – Location code  
- `DDD` – Branch code (optional)

Example: `DEUTDEFFXXX` (Deutsche Bank, Frankfurt).

---

## Use Cases
- **Cross-Border Payments**: Transfer of funds internationally between banks.
- **Securities Trading**: Instructions and confirmations for equity and bond transactions.
- **Treasury Transactions**: FX, derivatives, and liquidity management.
- **Trade Finance**: Letters of credit and guarantees.
- **Compliance**: Sanctions screening, AML alerts, and reporting.

---

## SWIFT in Compliance & KYC/AML
Financial institutions use SWIFT messages in workflows for:
- **Beneficial ownership tracing** (via payment flows and BICs).
- **AML monitoring** (identifying suspicious transfers).
- **Regulatory reporting** (cross-border transaction transparency).
- **OFAC/EU Sanctions checks** (flagging restricted parties).
- **Fraud Detection** (identity fraud, payment fraud).

---

## Example: MT103 Structure
```text
:20:  TRN12345678        # Transaction Reference Number
:23B: CRED               # Bank Operation Code
:32A: 250918USD12345,67  # Value Date (YYMMDD), Currency, Amount
:50K: /123456789
      JOHN DOE           # Ordering Customer
:59:  /987654321
      JANE SMITH         # Beneficiary Customer
:71A: OUR                # Details of Charges
