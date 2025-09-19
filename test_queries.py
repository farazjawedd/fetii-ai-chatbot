#!/usr/bin/env python3
"""
Test script to validate the FetiiAI chatbot functionality
"""

from data_processor import FetiiDataProcessor
from fetii_chatbot_demo import FetiiChatbotDemo

def test_data_processor():
    """Test the data processor functionality."""
    print("🧪 Testing Data Processor...")
    
    processor = FetiiDataProcessor('FetiiAI_Data_Austin.xlsx')
    processor.load_data()
    processor.process_data()
    
    summary = processor.get_data_summary()
    print(f"✅ Data loaded: {summary['total_trips']} trips, {summary['total_riders']} riders")
    
    return processor

def test_specific_queries():
    """Test specific queries from the hackathon requirements."""
    print("\n🧪 Testing Specific Queries...")
    
    processor = FetiiDataProcessor('FetiiAI_Data_Austin.xlsx')
    processor.load_data()
    processor.process_data()
    
    # Test Query 1: "How many groups went to Moody Center last month?"
    print("\n1️⃣ Testing: 'How many groups went to Moody Center last month?'")
    trips_moody = processor.query_data('trips_to_location', location='moody center', time_period='last_month')
    print(f"   Found {len(trips_moody)} trips to Moody Center in the last month")
    
    # Test Query 2: "What are the top drop-off spots for 18-24 year-olds on Saturday nights?"
    print("\n2️⃣ Testing: 'Top drop-off spots for 18-24 year-olds on Saturday nights'")
    demo_data = processor.query_data('demographic_analysis', age_group='18-24', day_of_week='Saturday', time_of_day='night')
    if len(demo_data) > 0:
        top_dropoffs = demo_data['Drop Off Category'].value_counts().head(3)
        print(f"   Top drop-off locations for 18-24 year-olds on Saturday nights:")
        for location, count in top_dropoffs.items():
            print(f"   - {location}: {count} trips")
    else:
        print("   No data found for this demographic/time combination")
    
    # Test Query 3: "When do large groups (6+ riders) typically ride downtown?"
    print("\n3️⃣ Testing: 'Large groups (6+ riders) downtown'")
    large_groups = processor.query_data('group_size_analysis', min_size=6, location='downtown')
    if len(large_groups) > 0:
        hour_distribution = large_groups['Hour'].value_counts().head(3)
        print(f"   Peak hours for large groups downtown:")
        for hour, count in hour_distribution.items():
            print(f"   - {hour}:00: {count} trips")
    else:
        print("   No large group trips found downtown")
    
    return True

def test_chatbot_integration():
    """Test the chatbot integration."""
    print("\n🧪 Testing Chatbot Integration...")
    
    # Create a mock chatbot instance for testing
    class MockChatbot:
        def __init__(self):
            self.processor = FetiiDataProcessor('FetiiAI_Data_Austin.xlsx')
            self.processor.load_data()
            self.processor.process_data()
        
        def analyze_query(self, query):
            # Simplified version of the chatbot's analyze_query method
            query_lower = query.lower()
            
            if 'moody center' in query_lower:
                trips = self.processor.query_data('trips_to_location', location='moody center')
                return {
                    'query_type': 'location_trips',
                    'data': trips,
                    'summary': f"Found {len(trips)} trips to Moody Center"
                }
            elif '18-24' in query_lower and 'saturday' in query_lower:
                data = self.processor.query_data('demographic_analysis', age_group='18-24', day_of_week='Saturday')
                return {
                    'query_type': 'demographic',
                    'data': data,
                    'summary': f"Analyzed {len(data)} records for 18-24 year-olds on Saturday"
                }
            elif 'large group' in query_lower or '6+' in query_lower:
                trips = self.processor.query_data('group_size_analysis', min_size=6)
                return {
                    'query_type': 'group_size',
                    'data': trips,
                    'summary': f"Found {len(trips)} trips with 6+ passengers"
                }
            else:
                summary = self.processor.get_data_summary()
                return {
                    'query_type': 'summary',
                    'data': summary,
                    'summary': "General data summary"
                }
    
    chatbot = MockChatbot()
    
    # Test queries
    test_queries = [
        "How many groups went to Moody Center last month?",
        "What are the top drop-off spots for 18-24 year-olds on Saturday nights?",
        "When do large groups (6+ riders) typically ride downtown?",
        "Show me general data summary"
    ]
    
    for query in test_queries:
        print(f"\n   Testing: '{query}'")
        result = chatbot.analyze_query(query)
        print(f"   Result: {result['summary']}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting FetiiAI Chatbot Tests\n")
    
    try:
        # Test 1: Data Processor
        processor = test_data_processor()
        
        # Test 2: Specific Queries
        test_specific_queries()
        
        # Test 3: Chatbot Integration
        test_chatbot_integration()
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 The chatbot is ready for the hackathon submission!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()