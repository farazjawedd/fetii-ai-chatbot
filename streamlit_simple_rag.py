import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import re
import numpy as np

load_dotenv()

class SimpleFetiiRAG:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.processed_data = None
        self.load_and_process_data()
    
    def load_and_process_data(self):
        """Load and process the Fetii data."""
        print("Loading and processing Fetii data...")
        
        # Load all sheets
        trip_data = pd.read_excel(self.excel_file_path, sheet_name='Trip Data')
        rider_data = pd.read_excel(self.excel_file_path, sheet_name="Checked in User ID's")
        demo_data = pd.read_excel(self.excel_file_path, sheet_name='Customer Demographics')
        
        # Convert trip date to datetime
        trip_data['Trip Date and Time'] = pd.to_datetime(trip_data['Trip Date and Time'])
        
        # Extract date/time components
        trip_data['Date'] = trip_data['Trip Date and Time'].dt.date
        trip_data['Time'] = trip_data['Trip Date and Time'].dt.time
        trip_data['Hour'] = trip_data['Trip Date and Time'].dt.hour
        trip_data['DayOfWeek'] = trip_data['Trip Date and Time'].dt.day_name()
        trip_data['Month'] = trip_data['Trip Date and Time'].dt.month
        trip_data['Year'] = trip_data['Trip Date and Time'].dt.year
        
        # Clean addresses
        trip_data['Pick Up Address Clean'] = trip_data['Pick Up Address'].apply(self._clean_address)
        trip_data['Drop Off Address Clean'] = trip_data['Drop Off Address'].apply(self._clean_address)
        
        # Extract location categories
        trip_data['Pick Up Category'] = trip_data['Pick Up Address Clean'].apply(self._categorize_location)
        trip_data['Drop Off Category'] = trip_data['Drop Off Address Clean'].apply(self._categorize_location)
        
        # Merge with demographic data
        # First rename the column to match
        trip_data = trip_data.rename(columns={'Booking User ID': 'User ID'})
        self.processed_data = trip_data.merge(demo_data, on='User ID', how='left')
        
        print(f"✅ Processed {len(self.processed_data)} records")
    
    def _clean_address(self, address):
        """Clean and standardize address."""
        if pd.isna(address):
            return "Unknown"
        return str(address).strip().lower()
    
    def _categorize_location(self, address):
        """Categorize location based on address."""
        if pd.isna(address) or address == "unknown":
            return "Unknown"
        
        address_lower = str(address).lower()
        
        if any(keyword in address_lower for keyword in ['downtown', '6th street', 'south congress', 'east 6th']):
            return "Downtown"
        elif any(keyword in address_lower for keyword in ['university', 'campus', 'ut austin', 'west campus']):
            return "University"
        elif any(keyword in address_lower for keyword in ['moody center', 'moody']):
            return "Moody Center"
        elif any(keyword in address_lower for keyword in ['airport', 'austin-bergstrom']):
            return "Airport"
        elif any(keyword in address_lower for keyword in ['domain', 'north austin']):
            return "North Austin"
        else:
            return "Other"
    
    def search_data(self, query, top_k=5):
        """Search for relevant data using simple text matching."""
        query_lower = query.lower()
        results = []
        
        # Search through all records
        for idx, row in self.processed_data.iterrows():
            score = 0
            
            # Check trip ID matches (highest priority)
            if any(keyword in query_lower for keyword in ['trip id', 'tripid', 'trip']):
                trip_id = self._extract_trip_id(query)
                if trip_id and row.get('Trip ID') == trip_id:
                    score += 20  # Highest priority for exact trip ID match
            
            # Check user ID matches
            if any(keyword in query_lower for keyword in ['user', 'age of user', 'userid']):
                user_id = self._extract_user_id(query)
                if user_id and row.get('User ID') == user_id:
                    score += 10
            
            # Check location matches
            if any(keyword in query_lower for keyword in ['moody center', 'downtown', 'university', 'airport']):
                location = self._extract_location(query)
                if location.lower() in str(row.get('Drop Off Address', '')).lower() or \
                   location.lower() in str(row.get('Drop Off Category', '')).lower():
                    score += 5
            
            # Check age group matches
            if any(keyword in query_lower for keyword in ['age', 'year old', '18-24', '25-34']):
                age_group = self._extract_age_group(query)
                if age_group and str(row.get('Age Group', '')).lower() == age_group.lower():
                    score += 5
            
            # Check day/time matches
            if any(keyword in query_lower for keyword in ['saturday', 'sunday', 'night', 'morning']):
                if 'saturday' in query_lower and row.get('DayOfWeek') == 'Saturday':
                    score += 3
                if 'sunday' in query_lower and row.get('DayOfWeek') == 'Sunday':
                    score += 3
                if 'night' in query_lower and row.get('Hour', 0) >= 18:
                    score += 3
            
            # Check group size matches
            if any(keyword in query_lower for keyword in ['large group', '6+', 'group size']):
                if row.get('Total Passengers', 0) >= 6:
                    score += 3
            
            if score > 0:
                results.append({
                    'score': score,
                    'data': row.to_dict(),
                    'index': idx
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _extract_trip_id(self, query):
        """Extract trip ID from query."""
        patterns = [
            r'trip\s+id\s+(\d+)',
            r'tripid\s+(\d+)',
            r'trip\s+(\d+)',
            r'(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_user_id(self, query):
        """Extract user ID from query."""
        patterns = [
            r'user\s+(\d+)',
            r'userid\s+(\d+)',
            r'user\s+id\s+(\d+)',
            r'age\s+of\s+user\s+(\d+)',
            r'(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        return None
    
    def _extract_location(self, query):
        """Extract location from query."""
        locations = ['moody center', 'downtown', 'university', 'airport', 'domain']
        
        for location in locations:
            if location in query.lower():
                return location.title()
        return "specified location"
    
    def _extract_age_group(self, query):
        """Extract age group from query."""
        query_lower = query.lower()
        
        if '18-24' in query_lower or '18 to 24' in query_lower:
            return '18-24'
        elif '25-34' in query_lower or '25 to 34' in query_lower:
            return '25-34'
        elif '35-44' in query_lower or '35 to 44' in query_lower:
            return '35-44'
        elif '45-54' in query_lower or '45 to 54' in query_lower:
            return '45-54'
        elif '55+' in query_lower or '55 and over' in query_lower:
            return '55+'
        
        return None
    
    def answer_question(self, question):
        """Answer a question using simple search."""
        results = self.search_data(question, top_k=5)
        
        if not results:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Generate answer based on results
        answer = self._generate_answer(question, results)
        
        return {
            'answer': answer,
            'sources': results,
            'confidence': results[0]['score'] / 10.0 if results else 0.0
        }
    
    def _generate_answer(self, question, results):
        """Generate answer from search results."""
        question_lower = question.lower()
        
        # Handle specific trip ID queries
        if any(keyword in question_lower for keyword in ['trip id', 'tripid', 'trip', 'details of this trip']):
            trip_id = self._extract_trip_id(question)
            if trip_id:
                trip_results = [r for r in results if r['data'].get('Trip ID') == trip_id]
                if trip_results:
                    data = trip_results[0]['data']
                    return f"""
                    **Trip ID {trip_id} Details:**
                    - Booking User ID: {data.get('User ID', 'Not available')}
                    - Pickup Address: {data.get('Pick Up Address', 'Not available')}
                    - Dropoff Address: {data.get('Drop Off Address', 'Not available')}
                    - Trip Date & Time: {data.get('Trip Date and Time', 'Not available')}
                    - Total Passengers: {data.get('Total Passengers', 'Not available')}
                    - Pickup Category: {data.get('Pick Up Category', 'Not available')}
                    - Dropoff Category: {data.get('Drop Off Category', 'Not available')}
                    - Day of Week: {data.get('DayOfWeek', 'Not available')}
                    - Hour: {data.get('Hour', 'Not available')}
                    - Age: {data.get('Age', 'Not available')}
                    - Age Group: {data.get('Age Group', 'Not available')}
                    """
                else:
                    return f"Sorry, I couldn't find any data for Trip ID {trip_id} in the Fetii dataset."
        
        # Handle specific user queries
        elif any(keyword in question_lower for keyword in ['age of user', 'user id', 'userid', 'user']):
            user_id = self._extract_user_id(question)
            if user_id:
                user_results = [r for r in results if r['data'].get('User ID') == user_id]
                if user_results:
                    data = user_results[0]['data']
                    return f"""
                    **User ID {user_id} Information:**
                    - Age: {data.get('Age', 'Not available')}
                    - Age Group: {data.get('Age Group', 'Not available')}
                    - Total Passengers: {data.get('Total Passengers', 'Not available')}
                    - Most Recent Trip: {data.get('Trip Date and Time', 'Not available')}
                    - Pickup: {data.get('Pick Up Address', 'Not available')}
                    - Dropoff: {data.get('Drop Off Address', 'Not available')}
                    - Pickup Category: {data.get('Pick Up Category', 'Not available')}
                    - Dropoff Category: {data.get('Drop Off Category', 'Not available')}
                    """
                else:
                    return f"Sorry, I couldn't find any data for User ID {user_id} in the Fetii dataset."
        
        # Handle location queries
        elif any(keyword in question_lower for keyword in ['went to', 'go to', 'trips to', 'groups to', 'moody center']):
            location = self._extract_location(question)
            location_results = [r for r in results if location.lower() in str(r['data'].get('Drop Off Address', '')).lower() or 
                              location.lower() in str(r['data'].get('Drop Off Category', '')).lower()]
            
            if location_results:
                total_trips = len(location_results)
                avg_passengers = np.mean([r['data'].get('Total Passengers', 0) for r in location_results if r['data'].get('Total Passengers')])
                
                return f"""
                **Trips to {location}:**
                - Total trips found: {total_trips}
                - Average group size: {avg_passengers:.1f} passengers
                - Date range: {min(r['data'].get('Trip Date and Time', '') for r in location_results)} to {max(r['data'].get('Trip Date and Time', '') for r in location_results)}
                """
            else:
                return f"No trips found to {location} in the dataset."
        
        # Handle demographic queries
        elif any(keyword in question_lower for keyword in ['age', 'year old', 'demographic']):
            age_groups = [r['data'].get('Age Group', '') for r in results if r['data'].get('Age Group')]
            age_group_counts = pd.Series(age_groups).value_counts()
            
            return f"""
            **Demographic Analysis:**
            - Age group distribution: {age_group_counts.to_dict()}
            - Total records analyzed: {len(results)}
            """
        
        # Default response
        return f"Based on the data, I found {len(results)} relevant records. Here are the key details from the most relevant match:\n\n{results[0]['data']}"

class FetiiSimpleRAGChatbot:
    def __init__(self):
        self.rag_system = None
        self.gemini_model = None
        self.setup_gemini()
        self.load_rag_system()
    
    def setup_gemini(self):
        """Setup Gemini AI client."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.warning("⚠️ Gemini API key not set. Using rule-based responses.")
            self.gemini_model = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                st.success("✅ Gemini AI connected!")
            except Exception as e:
                st.warning(f"⚠️ Gemini AI setup failed: {str(e)}. Using rule-based responses.")
                self.gemini_model = None
    
    def load_rag_system(self):
        """Load the simple RAG system."""
        st.info("🔄 Loading Fetii data...")
        self.rag_system = SimpleFetiiRAG('FetiiAI_Data_Austin.xlsx')
        st.success("✅ Data loaded successfully!")
    
    def generate_response(self, user_query):
        """Generate a response using simple RAG + Gemini AI."""
        if not self.rag_system:
            return "RAG system not available. Please refresh the page."
        
        # Get RAG results
        rag_result = self.rag_system.answer_question(user_query)
        
        if self.gemini_model is None:
            # Fallback to rule-based response
            return rag_result['answer']
        
        try:
            # Prepare context for Gemini
            context = f"""
            You are FetiiAI, a helpful assistant that answers questions about Fetii's rideshare data in Austin, TX.
            
            User Query: {user_query}
            
            RAG Analysis Result:
            - Answer: {rag_result['answer']}
            - Confidence: {rag_result['confidence']:.3f}
            - Sources Found: {len(rag_result['sources'])}
            
            Please provide a helpful, conversational response based on this data. Be specific about numbers and insights.
            Explain what the data means for Fetii's business. Keep the response concise but informative.
            """
            
            response = self.gemini_model.generate_content(context)
            return response.text
            
        except Exception as e:
            return f"I encountered an error generating a response: {str(e)}. Here's what I found: {rag_result['answer']}"

def main():
    st.set_page_config(
        page_title="FetiiAI Simple RAG Chatbot",
        page_icon="🚗",
        layout="wide"
    )
    
    st.title("🚗 FetiiAI Simple RAG Chatbot")
    st.markdown("Ask questions about Fetii's rideshare data using simple RAG (Retrieval-Augmented Generation)")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = FetiiSimpleRAGChatbot()
    
    chatbot = st.session_state.chatbot
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ About Simple RAG")
        st.markdown("""
        This chatbot uses **Simple RAG** to answer questions about Fetii's data:
        
        🔍 **Text Matching**: Finds relevant data using keyword matching
        🤖 **AI Generation**: Uses Gemini AI for natural responses
        📊 **Data Insights**: Provides specific answers from the dataset
        
        **Try these queries:**
        - "age of user 8794"
        - "How many groups went to Moody Center?"
        - "What are the top drop-off spots for 18-24 year-olds?"
        - "When do large groups typically ride downtown?"
        """)
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with FetiiAI")
        
        # Chat input
        user_input = st.text_input(
            "Ask a question about the Fetii data:",
            placeholder="e.g., age of user 8794, trips to Moody Center, demographic analysis...",
            key="user_input"
        )
        
        if st.button("🚀 Ask FetiiAI", type="primary") or user_input:
            if user_input:
                with st.spinner("🔍 Searching data and generating response..."):
                    # Generate response
                    response = chatbot.generate_response(user_input)
                    
                    # Display response
                    st.markdown("### 🤖 FetiiAI Response:")
                    st.markdown(response)
                    
                    # Get RAG results for visualization
                    rag_result = chatbot.rag_system.answer_question(user_input)
                    
                    # Show confidence score
                    if rag_result['confidence'] > 0:
                        st.metric("Confidence Score", f"{rag_result['confidence']:.3f}")
                    
                    # Show sources
                    if rag_result['sources']:
                        with st.expander(f"📚 Sources ({len(rag_result['sources'])} found)"):
                            for i, source in enumerate(rag_result['sources'][:3]):  # Show top 3
                                st.markdown(f"**Source {i+1}:** {source['data']}")
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        if chatbot.rag_system and chatbot.rag_system.processed_data is not None:
            df = chatbot.rag_system.processed_data
            
            # Basic stats
            st.metric("Total Trips", f"{len(df):,}")
            st.metric("Unique Users", f"{df['User ID'].nunique():,}")
            
            # Age distribution
            if 'Age Group' in df.columns:
                age_dist = df['Age Group'].value_counts()
                st.markdown("**Age Distribution:**")
                for age_group, count in age_dist.head(3).items():
                    st.markdown(f"- {age_group}: {count:,}")
            
            # Top locations
            if 'Drop Off Category' in df.columns:
                top_dropoffs = df['Drop Off Category'].value_counts().head(3)
                st.markdown("**Top Dropoff Locations:**")
                for location, count in top_dropoffs.items():
                    st.markdown(f"- {location}: {count:,}")
        
        st.subheader("🎯 Sample Queries")
        sample_queries = [
            "age of user 8794",
            "trips to Moody Center",
            "18-24 year olds Saturday night",
            "large groups downtown",
            "airport trips last month"
        ]
        
        for query in sample_queries:
            if st.button(f"💡 {query}", key=f"sample_{query}"):
                st.session_state.user_input = query
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("**FetiiAI Simple RAG Chatbot** - Powered by Text Search + Gemini AI")

if __name__ == "__main__":
    main()