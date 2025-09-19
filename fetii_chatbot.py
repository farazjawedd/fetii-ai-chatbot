import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from data_processor import FetiiDataProcessor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FetiiChatbot:
    def __init__(self):
        """Initialize the Fetii chatbot."""
        self.processor = None
        self.gemini_model = None
        self.setup_gemini()
        self.load_data()
        
    def setup_gemini(self):
        """Setup Gemini AI client."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "your_api_key_here":
            st.warning("⚠️ Gemini API key not set. Using demo mode with rule-based responses.")
            self.gemini_model = None
        else:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
    def load_data(self):
        """Load and process the Fetii data."""
        try:
            self.processor = FetiiDataProcessor('FetiiAI_Data_Austin.xlsx')
            self.processor.load_data()
            self.processor.process_data()
            st.success("✅ Data loaded successfully!")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.stop()
    
    def analyze_query(self, user_query):
        """Analyze the user query and determine what data to retrieve."""
        query_lower = user_query.lower()
        
        # Initialize result
        result = {
            'query_type': 'general',
            'data': None,
            'visualization': None,
            'summary': ''
        }
        
        try:
            # Check for specific query patterns
            
            # 1. Trips to specific location
            if any(keyword in query_lower for keyword in ['went to', 'go to', 'trips to', 'groups to']):
                location = self._extract_location(user_query)
                time_period = self._extract_time_period(user_query)
                
                trips = self.processor.query_data(
                    'trips_to_location',
                    location=location,
                    time_period=time_period
                )
                
                result['query_type'] = 'location_trips'
                result['data'] = trips
                result['summary'] = f"Found {len(trips)} trips to {location or 'specified location'}"
                
                # Create visualization
                if len(trips) > 0:
                    result['visualization'] = self._create_trip_visualization(trips, location)
            
            # 2. Demographic analysis (age groups, drop-off spots)
            elif any(keyword in query_lower for keyword in ['drop-off', 'dropoff', 'drop off', 'age', 'year old']):
                age_group = self._extract_age_group(user_query)
                day_of_week = self._extract_day_of_week(user_query)
                time_of_day = self._extract_time_of_day(user_query)
                
                data = self.processor.query_data(
                    'demographic_analysis',
                    age_group=age_group,
                    day_of_week=day_of_week,
                    time_of_day=time_of_day
                )
                
                result['query_type'] = 'demographic'
                result['data'] = data
                result['summary'] = f"Analyzed {len(data)} records for demographic patterns"
                
                # Create visualization
                if len(data) > 0:
                    result['visualization'] = self._create_demographic_visualization(data)
            
            # 3. Large group analysis
            elif any(keyword in query_lower for keyword in ['large group', '6+', 'big group', 'group size']):
                min_size = self._extract_group_size(user_query)
                location = self._extract_location(user_query)
                
                trips = self.processor.query_data(
                    'group_size_analysis',
                    min_size=min_size,
                    location=location
                )
                
                result['query_type'] = 'group_size'
                result['data'] = trips
                result['summary'] = f"Found {len(trips)} trips with {min_size}+ passengers"
                
                # Create visualization
                if len(trips) > 0:
                    result['visualization'] = self._create_group_size_visualization(trips)
            
            # 4. General data summary
            else:
                summary = self.processor.get_data_summary()
                result['query_type'] = 'summary'
                result['data'] = summary
                result['summary'] = "Here's a summary of the Fetii data"
        
        except Exception as e:
            result['summary'] = f"Error analyzing query: {str(e)}"
        
        return result
    
    def _extract_location(self, query):
        """Extract location from user query."""
        query_lower = query.lower()
        
        # Common Austin locations
        locations = {
            'moody center': 'moody center',
            'downtown': 'downtown',
            'campus': 'campus',
            'university': 'campus',
            '6th street': '6th street',
            'west campus': 'west campus',
            'east austin': 'east austin'
        }
        
        for key, value in locations.items():
            if key in query_lower:
                return value
        
        return None
    
    def _extract_time_period(self, query):
        """Extract time period from user query."""
        query_lower = query.lower()
        
        if 'last month' in query_lower or 'past month' in query_lower:
            return 'last_month'
        elif 'last week' in query_lower or 'past week' in query_lower:
            return 'last_week'
        elif 'yesterday' in query_lower:
            return 'yesterday'
        
        return 'all'
    
    def _extract_age_group(self, query):
        """Extract age group from user query."""
        query_lower = query.lower()
        
        if '18-24' in query_lower or '18 to 24' in query_lower:
            return '18-24'
        elif '25-30' in query_lower or '25 to 30' in query_lower:
            return '25-30'
        elif 'under 18' in query_lower:
            return 'Under 18'
        elif 'over 40' in query_lower:
            return 'Over 40'
        
        return None
    
    def _extract_day_of_week(self, query):
        """Extract day of week from user query."""
        query_lower = query.lower()
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            if day in query_lower:
                return day.capitalize()
        
        return None
    
    def _extract_time_of_day(self, query):
        """Extract time of day from user query."""
        query_lower = query.lower()
        
        if 'night' in query_lower or 'evening' in query_lower:
            return 'night'
        elif 'morning' in query_lower:
            return 'morning'
        elif 'afternoon' in query_lower:
            return 'afternoon'
        
        return None
    
    def _extract_group_size(self, query):
        """Extract minimum group size from user query."""
        import re
        
        # Look for patterns like "6+", "6 or more", "at least 6"
        numbers = re.findall(r'\d+', query)
        if numbers:
            return int(numbers[0])
        
        return 6  # Default to 6+ for large groups
    
    def _create_trip_visualization(self, trips, location):
        """Create visualization for trip data."""
        if len(trips) == 0:
            return None
        
        # Create a bar chart of trips by day
        trips_by_day = trips.groupby('Date').size().reset_index(name='Trip Count')
        
        fig = px.bar(
            trips_by_day,
            x='Date',
            y='Trip Count',
            title=f'Trips to {location or "Location"} Over Time',
            labels={'Date': 'Date', 'Trip Count': 'Number of Trips'}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Trips",
            showlegend=False
        )
        
        return fig
    
    def _create_demographic_visualization(self, data):
        """Create visualization for demographic data."""
        if len(data) == 0:
            return None
        
        # Create a pie chart of drop-off locations
        dropoff_counts = data['Drop Off Category'].value_counts()
        
        fig = px.pie(
            values=dropoff_counts.values,
            names=dropoff_counts.index,
            title='Top Drop-off Locations'
        )
        
        return fig
    
    def _create_group_size_visualization(self, trips):
        """Create visualization for group size data."""
        if len(trips) == 0:
            return None
        
        # Create a histogram of group sizes
        fig = px.histogram(
            trips,
            x='Total Passengers',
            title='Distribution of Group Sizes',
            labels={'Total Passengers': 'Group Size', 'count': 'Number of Trips'}
        )
        
        return fig
    
    def generate_response(self, user_query, analysis_result):
        """Generate a natural language response using Gemini AI or fallback to rule-based."""
        if self.gemini_model is None:
            # Fallback to rule-based response
            return self._generate_rule_based_response(user_query, analysis_result)
        
        try:
            # Prepare context for the AI
            context = f"""
            You are FetiiAI, a helpful assistant that answers questions about Fetii's rideshare data in Austin, TX.
            
            User Query: {user_query}
            
            Analysis Result:
            - Query Type: {analysis_result['query_type']}
            - Summary: {analysis_result['summary']}
            - Data Available: {analysis_result['data'] is not None}
            
            Please provide a helpful, conversational response about the Fetii data. Be specific about numbers and insights.
            If there's data available, mention the key findings. Keep the response concise but informative.
            """
            
            response = self.gemini_model.generate_content(context)
            return response.text
            
        except Exception as e:
            return f"I encountered an error generating a response: {str(e)}. Here's what I found: {analysis_result['summary']}"
    
    def _generate_rule_based_response(self, user_query, analysis_result):
        """Generate rule-based response when OpenAI is not available."""
        query_lower = user_query.lower()
        
        if analysis_result['query_type'] == 'location_trips':
            data = analysis_result['data']
            if data is not None and len(data) > 0:
                avg_passengers = data['Total Passengers'].mean()
                return f"""
                🎯 **Location Analysis Results**
                
                I found **{len(data)} trips** to the specified location in the Fetii dataset.
                
                **Key Insights:**
                - Average group size: {avg_passengers:.1f} passengers
                - Date range: {data['Date'].min()} to {data['Date'].max()}
                - Most common pickup area: {data['Pick Up Category'].mode().iloc[0] if len(data) > 0 else 'N/A'}
                
                This shows the demand patterns for this location in Austin!
                """
            else:
                return "I didn't find any trips to that location in the current dataset. Try asking about popular areas like Downtown, Campus, or Moody Center!"
        
        elif analysis_result['query_type'] == 'demographic':
            data = analysis_result['data']
            if data is not None and len(data) > 0:
                top_dropoffs = data['Drop Off Category'].value_counts().head(3)
                response = f"""
                👥 **Demographic Analysis Results**
                
                I analyzed **{len(data)} records** for the specified demographic group.
                
                **Top Drop-off Locations:**
                """
                for location, count in top_dropoffs.items():
                    response += f"\n- {location}: {count} trips"
                
                response += "\n\nThis shows where this age group prefers to go in Austin!"
                return response
            else:
                return "I didn't find data matching those demographic criteria. Try asking about 18-24 year olds or different time periods!"
        
        elif analysis_result['query_type'] == 'group_size':
            data = analysis_result['data']
            if data is not None and len(data) > 0:
                avg_size = data['Total Passengers'].mean()
                max_size = data['Total Passengers'].max()
                peak_hour = data['Hour'].mode().iloc[0] if len(data) > 0 else 'N/A'
                return f"""
                🚗 **Large Group Analysis Results**
                
                I found **{len(data)} trips** with large groups in the dataset.
                
                **Group Size Statistics:**
                - Average group size: {avg_size:.1f} passengers
                - Largest group: {max_size} passengers
                - Peak activity hour: {peak_hour}:00
                
                This shows when and where large groups are most active in Austin!
                """
            else:
                return "I didn't find any large group trips matching those criteria. Try asking about groups with 6+ passengers!"
        
        else:
            # General summary
            summary = analysis_result['data']
            return f"""
            📊 **Fetii Austin Data Overview**
            
            Here's what I found in the Fetii dataset:
            
            **Overall Statistics:**
            - Total trips: {summary['total_trips']:,}
            - Total riders: {summary['total_riders']:,}
            - Users with demographics: {summary['total_users_with_demographics']:,}
            - Date range: {summary['date_range']['start'].strftime('%Y-%m-%d')} to {summary['date_range']['end'].strftime('%Y-%m-%d')}
            
            **Popular Areas:**
            - Top pickup: {list(summary['top_pickup_locations'].keys())[0]} ({list(summary['top_pickup_locations'].values())[0]} trips)
            - Top dropoff: {list(summary['top_dropoff_locations'].keys())[0]} ({list(summary['top_dropoff_locations'].values())[0]} trips)
            
            Ask me specific questions about trips, demographics, or locations for more detailed insights!
            """

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="FetiiAI Chatbot",
        page_icon="🚗",
        layout="wide"
    )
    
    st.title("🚗 FetiiAI Chatbot")
    st.markdown("Ask me anything about Fetii's rideshare data in Austin, TX!")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner("Loading Fetii data..."):
            st.session_state.chatbot = FetiiChatbot()
    
    # Sidebar with example queries
    with st.sidebar:
        st.header("💡 Example Queries")
        example_queries = [
            "How many groups went to Moody Center last month?",
            "What are the top drop-off spots for 18-24 year-olds on Saturday nights?",
            "When do large groups (6+ riders) typically ride downtown?",
            "Show me trip patterns for West Campus",
            "What's the age distribution of riders?",
            "How many trips happened last week?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.user_input = query
        
        st.header("📊 Data Summary")
        if st.session_state.chatbot.processor:
            summary = st.session_state.chatbot.processor.get_data_summary()
            st.write(f"**Total Trips:** {summary['total_trips']:,}")
            st.write(f"**Total Riders:** {summary['total_riders']:,}")
            st.write(f"**Date Range:** {summary['date_range']['start'].strftime('%Y-%m-%d')} to {summary['date_range']['end'].strftime('%Y-%m-%d')}")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat input
        user_input = st.text_input(
            "Ask me about Fetii's data:",
            value=st.session_state.get('user_input', ''),
            placeholder="e.g., How many groups went to Moody Center last month?"
        )
        
        if st.button("Ask FetiiAI", type="primary") or user_input:
            if user_input:
                with st.spinner("Analyzing your question..."):
                    # Analyze the query
                    analysis_result = st.session_state.chatbot.analyze_query(user_input)
                    
                    # Generate response
                    response = st.session_state.chatbot.generate_response(user_input, analysis_result)
                    
                    # Display response
                    st.markdown("### 🤖 FetiiAI Response")
                    st.write(response)
                    
                    # Display visualization if available
                    if analysis_result['visualization']:
                        st.markdown("### 📊 Data Visualization")
                        st.plotly_chart(analysis_result['visualization'], use_container_width=True)
                    
                    # Display raw data if requested
                    if st.checkbox("Show raw data"):
                        if analysis_result['data'] is not None:
                            if isinstance(analysis_result['data'], dict):
                                st.json(analysis_result['data'])
                            else:
                                st.dataframe(analysis_result['data'])
                
                # Clear the input
                st.session_state.user_input = ''
    
    with col2:
        st.markdown("### 🎯 Quick Stats")
        if st.session_state.chatbot.processor:
            summary = st.session_state.chatbot.processor.get_data_summary()
            
            # Display key metrics
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("Total Trips", f"{summary['total_trips']:,}")
                st.metric("Total Riders", f"{summary['total_riders']:,}")
            
            with col2_2:
                st.metric("Users with Demographics", f"{summary['total_users_with_demographics']:,}")
            
            # Top locations
            st.markdown("**Top Pickup Locations:**")
            for location, count in list(summary['top_pickup_locations'].items())[:3]:
                st.write(f"• {location}: {count}")
            
            st.markdown("**Top Dropoff Locations:**")
            for location, count in list(summary['top_dropoff_locations'].items())[:3]:
                st.write(f"• {location}: {count}")

if __name__ == "__main__":
    main()