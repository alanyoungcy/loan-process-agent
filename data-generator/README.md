# Data Generator for Loan Agent System

## Overview
Generates realistic HK-localized demo data for the loan collection system.

## Features
- Hong Kong customer data (HKID, +852 phones, HK addresses)
- Realistic case scenarios
- Workflow instances linked to cases
- Contact history
- Payment records

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate 200 demo cases (default)
python seed.py

# Generate specific scenario
python seed.py --scenario demo_basic     # 100 cases
python seed.py --scenario demo_full      # 500 cases
python seed.py --scenario stress_test    # 10,000 cases

# Reset and regenerate
python seed.py --reset

# Custom count
python seed.py --count 200
```

## Directory Structure
```
data-generator/
├── generators/
│   ├── customers.py      # HK customer generator
│   ├── cases.py          # Collection cases
│   ├── workflows.py      # Workflow instances
│   ├── contacts.py       # Contact history
│   └── payments.py       # Payment records
├── templates/
│   ├── hk_names.json     # HK names (Cantonese/English)
│   ├── hk_addresses.json # HK districts and streets
│   └── loan_products.json # Loan types
├── scenarios/
│   ├── demo_basic.yaml
│   ├── demo_full.yaml
│   └── stress_test.yaml
├── seed.py              # Main seeding script
├── requirements.txt
└── README.md
```

## Data Generated

### Customers
- HKID format: A123456(7)
- Phone: +852 5xxx-xxxx / 6xxx-xxxx / 9xxx-xxxx
- Addresses: 18 HK districts
- Chinese and English names
- Credit scores: 300-850
- Risk levels: low, medium, high

### Cases
- Various overdue periods (1-365 days)
- Loan amounts: $5,000 - $500,000
- Linked to workflow instances
- Realistic status progression

### Workflows
- 6 workflow types matched to case scenarios
- Running and completed instances
- Current task tracking
