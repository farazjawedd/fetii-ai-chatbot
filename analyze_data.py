import pandas as pd

# Load the Excel file
xl = pd.ExcelFile('FetiiAI_Data_Austin.xlsx')
print("Sheet names:", xl.sheet_names)

# Analyze Trip Data
print("\n" + "="*50)
print("TRIP DATA ANALYSIS")
print("="*50)
trip_data = pd.read_excel('FetiiAI_Data_Austin.xlsx', sheet_name='Trip Data')
print(f"Shape: {trip_data.shape}")
print(f"Columns: {trip_data.columns.tolist()}")
print("\nFirst 3 rows:")
print(trip_data.head(3))
print(f"\nData types:")
print(trip_data.dtypes)
print(f"\nSample pickup addresses:")
print(trip_data['Pick Up Address'].head(10).tolist())
print(f"\nSample dropoff addresses:")
print(trip_data['Drop Off Address'].head(10).tolist())

# Analyze Checked in User IDs
print("\n" + "="*50)
print("CHECKED IN USER IDs ANALYSIS")
print("="*50)
rider_data = pd.read_excel('FetiiAI_Data_Austin.xlsx', sheet_name="Checked in User ID's")
print(f"Shape: {rider_data.shape}")
print(f"Columns: {rider_data.columns.tolist()}")
print("\nFirst 3 rows:")
print(rider_data.head(3))
print(f"\nData types:")
print(rider_data.dtypes)

# Analyze Customer Demographics
print("\n" + "="*50)
print("CUSTOMER DEMOGRAPHICS ANALYSIS")
print("="*50)
demo_data = pd.read_excel('FetiiAI_Data_Austin.xlsx', sheet_name='Customer Demographics')
print(f"Shape: {demo_data.shape}")
print(f"Columns: {demo_data.columns.tolist()}")
print("\nFirst 3 rows:")
print(demo_data.head(3))
print(f"\nData types:")
print(demo_data.dtypes)
print(f"\nAge distribution:")
print(demo_data['Age'].value_counts().head(10))