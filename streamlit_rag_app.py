import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from rag_system import FetiiRAGSystem
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class FetiiRAGChatbot:
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
        """Load or create the RAG system."""
        if os.path.exists('fetii_rag_system.pkl'):
            st.info("🔄 Loading existing RAG system...")
            self.rag_system = FetiiRAGSystem('FetiiAI_Data_Austin.xlsx')
            if self.rag_system.load_system('fetii_rag_system.pkl'):
                st.success("✅ RAG system loaded successfully!")
            else:
                st.error("❌ Failed to load RAG system. Creating new one...")
                self._create_new_rag_system()
        else:
            st.info("🔄 Creating new RAG system...")
            self._create_new_rag_system()
    
    def _create_new_rag_system(self):
        """Create a new RAG system from scratch."""
        with st.spinner("Creating RAG system... This may take a few minutes."):
            self.rag_system = FetiiRAGSystem('FetiiAI_Data_Austin.xlsx')
            self.rag_system.load_and_process_data()
            self.rag_system.create_data_chunks()
            self.rag_system.create_embeddings()
            self.rag_system.save_system('fetii_rag_system.pkl')
            st.success("✅ RAG system created and saved!")
    
    def generate_response(self, user_query):
        """Generate a response using RAG + Gemini AI."""
        if not self.rag_system:
            return "RAG system not available. Please refresh the page."
        
        # Get RAG results
        rag_result = self.rag_system.answer_question(user_query, top_k=5)
        
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
    
    def create_visualization(self, rag_result):
        """Create visualizations based on RAG results."""
        if not rag_result['sources']:
            return None
        
        sources = rag_result['sources']
        
        # Create a DataFrame from sources
        df = pd.DataFrame(sources)
        
        if len(df) == 0:
            return None
        
        # Create visualizations based on data
        visualizations = []
        
        # Age group distribution
        if 'age_group' in df.columns and df['age_group'].notna().any():
            age_counts = df['age_group'].value_counts()
            if len(age_counts) > 0:
                fig_age = px.bar(
                    x=age_counts.index, 
                    y=age_counts.values,
                    title="Age Group Distribution",
                    labels={'x': 'Age Group', 'y': 'Count'}
                )
                visualizations.append(("Age Groups", fig_age))
        
        # Pickup/Dropoff categories
        if 'pickup_category' in df.columns and df['pickup_category'].notna().any():
            pickup_counts = df['pickup_category'].value_counts()
            if len(pickup_counts) > 0:
                fig_pickup = px.pie(
                    values=pickup_counts.values,
                    names=pickup_counts.index,
                    title="Pickup Locations"
                )
                visualizations.append(("Pickup Locations", fig_pickup))
        
        if 'dropoff_category' in df.columns and df['dropoff_category'].notna().any():
            dropoff_counts = df['dropoff_category'].value_counts()
            if len(dropoff_counts) > 0:
                fig_dropoff = px.pie(
                    values=dropoff_counts.values,
                    names=dropoff_counts.index,
                    title="Dropoff Locations"
                )
                visualizations.append(("Dropoff Locations", fig_dropoff))
        
        # Time analysis
        if 'hour' in df.columns and df['hour'].notna().any():
            hour_counts = df['hour'].value_counts().sort_index()
            if len(hour_counts) > 0:
                fig_hour = px.bar(
                    x=hour_counts.index,
                    y=hour_counts.values,
                    title="Trip Distribution by Hour",
                    labels={'x': 'Hour of Day', 'y': 'Number of Trips'}
                )
                visualizations.append(("Hourly Distribution", fig_hour))
        
        return visualizations

def main():
    st.set_page_config(
        page_title="FetiiAI RAG Chatbot",
        page_icon="🚗",
        layout="wide"
    )
    
    st.title("🚗 FetiiAI RAG Chatbot")
    st.markdown("Ask questions about Fetii's rideshare data using advanced RAG (Retrieval-Augmented Generation)")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = FetiiRAGChatbot()
    
    chatbot = st.session_state.chatbot
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ About RAG")
        st.markdown("""
        This chatbot uses **RAG (Retrieval-Augmented Generation)** to answer questions about Fetii's data:
        
        🔍 **Semantic Search**: Finds relevant data using AI embeddings
        🤖 **AI Generation**: Uses Gemini AI for natural responses
        📊 **Data Insights**: Provides specific answers from the dataset
        
        **Try these queries:**
        - "age of user 8794"
        - "How many groups went to Moody Center?"
        - "What are the top drop-off spots for 18-24 year-olds?"
        - "When do large groups typically ride downtown?"
        """)
        
        if st.button("🔄 Refresh RAG System"):
            if os.path.exists('fetii_rag_system.pkl'):
                os.remove('fetii_rag_system.pkl')
            st.session_state.chatbot = FetiiRAGChatbot()
            st.rerun()
    
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
                    rag_result = chatbot.rag_system.answer_question(user_input, top_k=5)
                    
                    # Show confidence score
                    if rag_result['confidence'] > 0:
                        st.metric("Confidence Score", f"{rag_result['confidence']:.3f}")
                    
                    # Show sources
                    if rag_result['sources']:
                        with st.expander(f"📚 Sources ({len(rag_result['sources'])} found)"):
                            for i, source in enumerate(rag_result['sources'][:3]):  # Show top 3
                                st.markdown(f"**Source {i+1}:** {source['text'][:200]}...")
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        if chatbot.rag_system and chatbot.rag_system.data_chunks:
            total_chunks = len(chatbot.rag_system.data_chunks)
            st.metric("Data Chunks", f"{total_chunks:,}")
            
            if chatbot.rag_system.processed_data is not None:
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
    st.markdown("**FetiiAI RAG Chatbot** - Powered by Vector Search + Gemini AI")

if __name__ == "__main__":
    main()