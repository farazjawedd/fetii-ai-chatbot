import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class FetiiDataProcessor:
    def __init__(self, excel_file_path):
        """Initialize the data processor with the Excel file path."""
        self.excel_file_path = excel_file_path
        self.trip_data = None
        self.rider_data = None
        self.demo_data = None
        self.processed_data = None
        
    def load_data(self):
        """Load all three sheets from the Excel file."""
        print("Loading data from Excel file...")
        
        # Load Trip Data
        self.trip_data = pd.read_excel(self.excel_file_path, sheet_name='Trip Data')
        print(f"Loaded {len(self.trip_data)} trip records")
        
        # Load Rider Data (Checked in User IDs)
        self.rider_data = pd.read_excel(self.excel_file_path, sheet_name="Checked in User ID's")
        print(f"Loaded {len(self.rider_data)} rider records")
        
        # Load Customer Demographics
        self.demo_data = pd.read_excel(self.excel_file_path, sheet_name='Customer Demographics')
        print(f"Loaded {len(self.demo_data)} demographic records")
        
    def process_data(self):
        """Process and clean the data, creating a comprehensive dataset."""
        print("Processing and cleaning data...")
        
        # Convert trip date to datetime
        self.trip_data['Trip Date and Time'] = pd.to_datetime(self.trip_data['Trip Date and Time'])
        
        # Extract date and time components
        self.trip_data['Date'] = self.trip_data['Trip Date and Time'].dt.date
        self.trip_data['Time'] = self.trip_data['Trip Date and Time'].dt.time
        self.trip_data['Hour'] = self.trip_data['Trip Date and Time'].dt.hour
        self.trip_data['DayOfWeek'] = self.trip_data['Trip Date and Time'].dt.day_name()
        self.trip_data['Month'] = self.trip_data['Trip Date and Time'].dt.month
        self.trip_data['Year'] = self.trip_data['Trip Date and Time'].dt.year
        
        # Clean and standardize addresses
        self.trip_data['Pick Up Address Clean'] = self.trip_data['Pick Up Address'].apply(self._clean_address)
        self.trip_data['Drop Off Address Clean'] = self.trip_data['Drop Off Address'].apply(self._clean_address)
        
        # Extract location categories
        self.trip_data['Pick Up Category'] = self.trip_data['Pick Up Address Clean'].apply(self._categorize_location)
        self.trip_data['Drop Off Category'] = self.trip_data['Drop Off Address Clean'].apply(self._categorize_location)
        
        # Merge with rider data to get all passengers per trip
        trip_with_riders = self.trip_data.merge(
            self.rider_data, 
            on='Trip ID', 
            how='left'
        )
        
        # Merge with demographic data
        self.processed_data = trip_with_riders.merge(
            self.demo_data, 
            on='User ID', 
            how='left'
        )
        
        # Create age groups
        self.processed_data['Age Group'] = self.processed_data['Age'].apply(self._get_age_group)
        
        # Create group size categories
        self.processed_data['Group Size Category'] = self.processed_data['Total Passengers'].apply(self._get_group_size_category)
        
        print(f"Processed data shape: {self.processed_data.shape}")
        
    def _clean_address(self, address):
        """Clean and standardize address strings."""
        if pd.isna(address):
            return "Unknown"
        
        address = str(address).strip()
        
        # Remove common suffixes and clean up
        address = re.sub(r',\s*Austin,?\s*TX,?\s*USA?', '', address, flags=re.IGNORECASE)
        address = re.sub(r',\s*United States,?\s*\d{5}', '', address, flags=re.IGNORECASE)
        address = re.sub(r',\s*Austin,?\s*United States,?\s*\d{5}', '', address, flags=re.IGNORECASE)
        
        return address.strip()
    
    def _categorize_location(self, address):
        """Categorize locations based on address patterns."""
        if pd.isna(address) or address == "Unknown":
            return "Unknown"
        
        address_lower = address.lower()
        
        # Campus/University locations
        if any(keyword in address_lower for keyword in ['campus', 'university', 'ut', 'college']):
            return "Campus/University"
        
        # Downtown locations
        if any(keyword in address_lower for keyword in ['downtown', '6th street', '6th st', 'congress']):
            return "Downtown"
        
        # Entertainment venues
        if any(keyword in address_lower for keyword in ['moody center', 'moody', 'stadium', 'arena', 'theater', 'theatre']):
            return "Entertainment Venue"
        
        # Bars/Clubs
        if any(keyword in address_lower for keyword in ['bar', 'club', 'pub', 'tavern', 'lounge']):
            return "Bar/Club"
        
        # Restaurants
        if any(keyword in address_lower for keyword in ['restaurant', 'cafe', 'grill', 'kitchen', 'burrito', 'pizza']):
            return "Restaurant"
        
        # Residential
        if any(keyword in address_lower for keyword in ['apartment', 'house', 'villa', 'residence', 'home']):
            return "Residential"
        
        # Shopping
        if any(keyword in address_lower for keyword in ['mall', 'shopping', 'market', 'store']):
            return "Shopping"
        
        return "Other"
    
    def _get_age_group(self, age):
        """Categorize age into groups."""
        if pd.isna(age):
            return "Unknown"
        
        age = float(age)
        if age < 18:
            return "Under 18"
        elif age <= 24:
            return "18-24"
        elif age <= 30:
            return "25-30"
        elif age <= 40:
            return "31-40"
        else:
            return "Over 40"
    
    def _get_group_size_category(self, size):
        """Categorize group sizes."""
        if pd.isna(size):
            return "Unknown"
        
        size = int(size)
        if size == 1:
            return "Solo"
        elif size <= 3:
            return "Small (2-3)"
        elif size <= 5:
            return "Medium (4-5)"
        elif size <= 7:
            return "Large (6-7)"
        else:
            return "Very Large (8+)"
    
    def get_data_summary(self):
        """Get a summary of the processed data."""
        if self.processed_data is None:
            return "Data not processed yet. Call process_data() first."
        
        summary = {
            'total_trips': len(self.trip_data),
            'total_riders': len(self.rider_data),
            'total_users_with_demographics': len(self.demo_data),
            'date_range': {
                'start': self.trip_data['Trip Date and Time'].min(),
                'end': self.trip_data['Trip Date and Time'].max()
            },
            'top_pickup_locations': self.trip_data['Pick Up Category'].value_counts().head(5).to_dict(),
            'top_dropoff_locations': self.trip_data['Drop Off Category'].value_counts().head(5).to_dict(),
            'age_distribution': self.processed_data['Age Group'].value_counts().to_dict(),
            'group_size_distribution': self.processed_data['Group Size Category'].value_counts().to_dict()
        }
        
        return summary
    
    def query_data(self, query_type, **kwargs):
        """Query the processed data based on different criteria."""
        if self.processed_data is None:
            return "Data not processed yet. Call process_data() first."
        
        df = self.processed_data.copy()
        
        if query_type == "trips_to_location":
            location = kwargs.get('location', '').lower()
            time_period = kwargs.get('time_period', 'all')
            
            # Filter by location
            if location:
                df = df[df['Drop Off Address Clean'].str.lower().str.contains(location, na=False)]
            
            # Filter by time period
            if time_period == 'last_month':
                cutoff_date = datetime.now() - timedelta(days=30)
                df = df[df['Trip Date and Time'] >= cutoff_date]
            elif time_period == 'last_week':
                cutoff_date = datetime.now() - timedelta(days=7)
                df = df[df['Trip Date and Time'] >= cutoff_date]
            
            return df.groupby('Trip ID').first()  # Get unique trips
        
        elif query_type == "demographic_analysis":
            age_group = kwargs.get('age_group', '')
            day_of_week = kwargs.get('day_of_week', '')
            time_of_day = kwargs.get('time_of_day', '')
            
            # Filter by age group
            if age_group:
                df = df[df['Age Group'] == age_group]
            
            # Filter by day of week
            if day_of_week:
                df = df[df['DayOfWeek'] == day_of_week]
            
            # Filter by time of day
            if time_of_day == 'night':
                df = df[df['Hour'].between(18, 23)]
            elif time_of_day == 'morning':
                df = df[df['Hour'].between(6, 11)]
            elif time_of_day == 'afternoon':
                df = df[df['Hour'].between(12, 17)]
            
            return df
        
        elif query_type == "group_size_analysis":
            min_size = kwargs.get('min_size', 6)
            location = kwargs.get('location', '')
            
            # Filter by group size
            df = df[df['Total Passengers'] >= min_size]
            
            # Filter by location if specified
            if location:
                location_lower = location.lower()
                if 'downtown' in location_lower:
                    df = df[df['Drop Off Category'] == 'Downtown']
                else:
                    df = df[df['Drop Off Address Clean'].str.lower().str.contains(location, na=False)]
            
            return df.groupby('Trip ID').first()  # Get unique trips
        
        return df

# Example usage
if __name__ == "__main__":
    processor = FetiiDataProcessor('FetiiAI_Data_Austin.xlsx')
    processor.load_data()
    processor.process_data()
    
    summary = processor.get_data_summary()
    print("\nData Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")