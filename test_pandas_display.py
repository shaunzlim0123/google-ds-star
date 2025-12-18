import pandas as pd

# Create a simple test with 7 countries
data = {'country': ['US', 'GB', 'CA', 'DE', 'FR', 'JP', 'AU'], 
        'avg_amount': [1500, 1200, 800, 900, 1100, 1600, 700]}
df = pd.DataFrame(data)

print("Default display:")
print(df)

print("\n\nWith display options:")
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(df)
