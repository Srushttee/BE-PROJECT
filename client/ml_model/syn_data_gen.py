
'''
import random
import pandas as pd

months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

# Tariff Slab Definitions (based on FY 2025–26)
def calculate_tariff(units, region):
    wheeling_charge = 1.20
    fixed_charge = 128 if region == 'rural' else 130

    # Slab-wise energy charges (use mid-range of provided values)
    if units <= 100:
        energy_charge = 5.32  # mid of 4.32–6.32
    elif units <= 300:
        energy_charge = 10.82  # mid of 9.40–12.23
    elif units <= 500:
        energy_charge = 14.64  # mid of 12.51–16.77
    else:
        energy_charge = 16.45  # mid of 13.97–18.93

    total_energy_cost = units * (energy_charge + wheeling_charge)
    total_bill = round(total_energy_cost + fixed_charge, 2)

    return total_bill

# Random unit generator based on region, appliances, and seasonal month
def generate_units(region, num_appliances, month):
    base_usage = 8 if region == 'rural' else 10

    # Seasonal multiplier
    if month in ['Apr', 'May', 'Jun']:
        seasonal_factor = random.uniform(1.15, 1.35)
    elif month in ['Dec', 'Jan']:
        seasonal_factor = random.uniform(0.85, 0.95)
    else:
        seasonal_factor = random.uniform(0.95, 1.05)

    fluctuation = random.uniform(0.9, 1.1)

    units = int(num_appliances * base_usage * seasonal_factor * fluctuation)
    return max(units, 20)

def generate_tariff_data(num_customers=400, start_year=2015, end_year=2024):
    data = []
    for customer_id in range(1, num_customers + 1):
        region = random.choice(['rural', 'urban'])
        #household_size = random.randint(2, 12)
        #num_appliances = random.randint(4, 12) if region == 'rural' else random.randint(10, 25)
        num_appliances = 4

        for year in range(start_year, end_year + 1):
            for month in months:
                units = generate_units(region, num_appliances, month)
                bill = calculate_tariff(units, region)

                data.append({
                    'customer_id': f"CUST{customer_id:04d}",
                    'region': region,
                    'year': year,
                    'month': month,
                 #  'household_size': household_size,
                    'num_appliances': num_appliances,
                    'units_consumed_kwh': units,
                    'billing_amount_inr': bill
                })

    return pd.DataFrame(data)

# Generate the full dataset
df = generate_tariff_data()
print(df.head(13))
#df.to_csv("electricity_tariff_clean.csv", index=False)
'''