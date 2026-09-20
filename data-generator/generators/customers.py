"""
Customer Generator - HK Localized Customer Data
"""
import random
from faker import Faker
from typing import Dict
import json
import os

class CustomerGenerator:
    def __init__(self):
        self.faker_en = Faker('en_US')  # Use en_US instead of en_HK
        self.faker_zh = Faker('zh_CN')  # Chinese names

        # Load HK data templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        with open(os.path.join(template_dir, 'hk_names.json'), 'r', encoding='utf-8') as f:
            self.name_data = json.load(f)
        with open(os.path.join(template_dir, 'hk_addresses.json'), 'r', encoding='utf-8') as f:
            self.address_data = json.load(f)

    def generate_hkid(self) -> str:
        """Generate realistic HKID: A123456(7)"""
        letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        digits = random.randint(100000, 999999)
        # Simplified check digit calculation
        check_digit = random.randint(0, 9)
        return f"{letter}{digits}({check_digit})"

    def generate_phone(self) -> str:
        """Generate +852 mobile number"""
        prefix = random.choice(['5', '6', '9'])  # HK mobile prefixes
        number = random.randint(1000000, 9999999)
        return f"+852{prefix}{number}"

    def generate_english_name(self) -> str:
        """Generate English name"""
        return random.choice(self.name_data['english_given_names']) + ' ' + \
               random.choice(self.name_data['english_surnames'])

    def generate_cantonese_name(self) -> str:
        """Generate Cantonese name"""
        surname = random.choice(self.name_data['cantonese_surnames'])
        given_name = random.choice(self.name_data['cantonese_given_names'])
        return f"{surname}{given_name}"

    def generate_hk_address(self) -> Dict[str, str]:
        """Generate HK address"""
        district = random.choice(self.address_data['districts'])
        street = random.choice(self.address_data['streets'])
        building_number = random.randint(1, 999)
        floor = random.randint(1, 50)
        flat = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])

        return {
            'full_address': f"Flat {flat}, {floor}/F, {building_number} {street}, {district}, Hong Kong",
            'district': district,
            'street': street
        }

    def generate_customer(self, customer_id: str = None) -> Dict:
        """Generate complete customer record"""
        if customer_id is None:
            customer_id = f"CUST{random.randint(10000, 99999)}"

        address = self.generate_hk_address()

        return {
            'customer_id': customer_id,
            'name_en': self.generate_english_name(),
            'name_zh': self.generate_cantonese_name(),
            'hkid': self.generate_hkid(),
            'phone': self.generate_phone(),
            'email': self.faker_en.email(),
            'address': address['full_address'],
            'district': address['district'],
            'credit_score': random.randint(300, 850),
            'risk_level': random.choices(
                ['low', 'medium', 'high'],
                weights=[50, 35, 15]
            )[0],
            'customer_segment': random.choices(
                ['standard', 'premium', 'VIP', 'high_risk'],
                weights=[60, 25, 10, 5]
            )[0]
        }
