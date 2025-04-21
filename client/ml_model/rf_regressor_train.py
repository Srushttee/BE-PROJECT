# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

# Load generated data
df = pd.read_csv("D:\python based projects\ML data\electricity_tariff_fy25_clean.csv")

# Sort for next month billing prediction
df = df.sort_values(by=['customer_id', 'year', 'month'])

# Map months to numeric
month_map = {month: i+1 for i, month in enumerate([
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
])}
df['month_num'] = df['month'].map(month_map)

# Encode region
df['region_encoded'] = LabelEncoder().fit_transform(df['region'])

# Shift billing_amount to next row per customer to use as target
df['next_month_bill'] = df.groupby('customer_id')['billing_amount_inr'].shift(-1)

# Drop rows where next month's bill is NaN (i.e. last month)
df = df.dropna()

# Features and target
features = ['region_encoded', 'year', 'month_num', 'household_size', 'num_appliances', 'units_consumed_kwh']
X = df[features]
y = df['next_month_bill']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
#joblib.dump(model,'billing_predictor_model.pkl')
print("✅ Model trained and saved as billing_predictor_model.pkl")