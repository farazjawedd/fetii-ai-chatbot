import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from typing import List, Dict, Any
import re

class FetiiRAGSystem:
    def __init__(self, excel_file_path: str):
        """Initialize the RAG system with Fetii data."""
        self.excel_file_path = excel_file_path
        self.model = None
        self.index = None
        self.data_chunks = []
        self.embeddings = None
        self.processed_data = None
        
        # Load the embedding model
        self._load_model()
        
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded sentence transformer model")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def load_and_process_data(self):
        """Load and process the Fetii data for RAG."""
        print("Loading and processing Fetii data for RAG...")
        
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
    
    def create_data_chunks(self):
        """Create searchable chunks from the processed data."""
        print("Creating data chunks for RAG...")
        
        self.data_chunks = []
        
        # Create chunks for each trip record
        for idx, row in self.processed_data.iterrows():
            # Create a comprehensive text representation of each record
            chunk_text = self._create_chunk_text(row)
            
            chunk = {
                'id': idx,
                'text': chunk_text,
                'trip_id': row.get('Trip ID', ''),
                'user_id': row.get('User ID', ''),
                'age': row.get('Age', ''),
                'age_group': row.get('Age Group', ''),
                'pickup_address': row.get('Pick Up Address', ''),
                'dropoff_address': row.get('Drop Off Address', ''),
                'pickup_category': row.get('Pick Up Category', ''),
                'dropoff_category': row.get('Drop Off Category', ''),
                'total_passengers': row.get('Total Passengers', ''),
                'trip_date': row.get('Trip Date and Time', ''),
                'day_of_week': row.get('DayOfWeek', ''),
                'hour': row.get('Hour', ''),
                'month': row.get('Month', ''),
                'year': row.get('Year', ''),
                'raw_data': row.to_dict()
            }
            
            self.data_chunks.append(chunk)
        
        print(f"✅ Created {len(self.data_chunks)} data chunks")
    
    def _create_chunk_text(self, row):
        """Create a comprehensive text representation of a data row."""
        text_parts = []
        
        # Basic trip info
        text_parts.append(f"Trip ID: {row.get('Trip ID', 'N/A')}")
        text_parts.append(f"User ID: {row.get('User ID', 'N/A')}")
        text_parts.append(f"Total Passengers: {row.get('Total Passengers', 'N/A')}")
        
        # Demographics
        if pd.notna(row.get('Age')):
            text_parts.append(f"Age: {row.get('Age')}")
        if pd.notna(row.get('Age Group')):
            text_parts.append(f"Age Group: {row.get('Age Group')}")
        
        # Location info
        text_parts.append(f"Pickup: {row.get('Pick Up Address', 'N/A')}")
        text_parts.append(f"Dropoff: {row.get('Drop Off Address', 'N/A')}")
        text_parts.append(f"Pickup Category: {row.get('Pick Up Category', 'N/A')}")
        text_parts.append(f"Dropoff Category: {row.get('Drop Off Category', 'N/A')}")
        
        # Time info
        if pd.notna(row.get('Trip Date and Time')):
            text_parts.append(f"Date: {row.get('Trip Date and Time')}")
        if pd.notna(row.get('DayOfWeek')):
            text_parts.append(f"Day: {row.get('DayOfWeek')}")
        if pd.notna(row.get('Hour')):
            text_parts.append(f"Hour: {row.get('Hour')}")
        if pd.notna(row.get('Month')):
            text_parts.append(f"Month: {row.get('Month')}")
        if pd.notna(row.get('Year')):
            text_parts.append(f"Year: {row.get('Year')}")
        
        return " | ".join(text_parts)
    
    def create_embeddings(self):
        """Create embeddings for all data chunks."""
        if not self.model:
            print("❌ Model not loaded")
            return
        
        print("Creating embeddings...")
        
        # Extract text from chunks
        texts = [chunk['text'] for chunk in self.data_chunks]
        
        # Create embeddings
        self.embeddings = self.model.encode(texts)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        print(f"✅ Created embeddings and FAISS index with {self.index.ntotal} vectors")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant data chunks using semantic similarity."""
        if not self.model or not self.index:
            print("❌ RAG system not initialized")
            return []
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.data_chunks):
                result = self.data_chunks[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results
    
    def answer_question(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG."""
        # Search for relevant data
        relevant_chunks = self.search(question, top_k)
        
        if not relevant_chunks:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Extract specific information based on question type
        answer = self._extract_answer(question, relevant_chunks)
        
        return {
            'answer': answer,
            'sources': relevant_chunks,
            'confidence': relevant_chunks[0]['similarity_score'] if relevant_chunks else 0.0
        }
    
    def _extract_answer(self, question: str, chunks: List[Dict]) -> str:
        """Extract specific answer from relevant chunks."""
        question_lower = question.lower()
        
        # Handle specific user queries
        if any(keyword in question_lower for keyword in ['age of user', 'user id', 'userid', 'user']):
            user_id = self._extract_user_id(question)
            if user_id:
                user_chunks = [chunk for chunk in chunks if chunk.get('user_id') == user_id]
                if user_chunks:
                    chunk = user_chunks[0]
                    return f"""
                    **User ID {user_id} Information:**
                    - Age: {chunk.get('age', 'Not available')}
                    - Age Group: {chunk.get('age_group', 'Not available')}
                    - Total Passengers: {chunk.get('total_passengers', 'Not available')}
                    - Most Recent Trip: {chunk.get('trip_date', 'Not available')}
                    - Common Pickup: {chunk.get('pickup_category', 'Not available')}
                    - Common Dropoff: {chunk.get('dropoff_category', 'Not available')}
                    - Pickup Address: {chunk.get('pickup_address', 'Not available')}
                    - Dropoff Address: {chunk.get('dropoff_address', 'Not available')}
                    """
                else:
                    return f"Sorry, I couldn't find any data for User ID {user_id} in the Fetii dataset."
        
        # Handle location queries
        elif any(keyword in question_lower for keyword in ['went to', 'go to', 'trips to', 'groups to', 'moody center']):
            location = self._extract_location(question)
            location_chunks = [chunk for chunk in chunks if location.lower() in chunk.get('dropoff_address', '').lower() or 
                             location.lower() in chunk.get('dropoff_category', '').lower()]
            
            if location_chunks:
                total_trips = len(location_chunks)
                avg_passengers = np.mean([chunk.get('total_passengers', 0) for chunk in location_chunks if chunk.get('total_passengers')])
                
                return f"""
                **Trips to {location}:**
                - Total trips found: {total_trips}
                - Average group size: {avg_passengers:.1f} passengers
                - Date range: {min(chunk.get('trip_date', '') for chunk in location_chunks)} to {max(chunk.get('trip_date', '') for chunk in location_chunks)}
                """
            else:
                return f"No trips found to {location} in the dataset."
        
        # Handle demographic queries
        elif any(keyword in question_lower for keyword in ['age', 'year old', 'demographic']):
            age_chunks = chunks
            if age_chunks:
                age_groups = [chunk.get('age_group', '') for chunk in age_chunks if chunk.get('age_group')]
                age_group_counts = pd.Series(age_groups).value_counts()
                
                return f"""
                **Demographic Analysis:**
                - Age group distribution: {age_group_counts.to_dict()}
                - Total records analyzed: {len(age_chunks)}
                """
        
        # Default response
        return f"Based on the data, I found {len(chunks)} relevant records. Here are the key details from the most relevant match:\n\n{chunks[0]['text']}"
    
    def _extract_user_id(self, question: str) -> int:
        """Extract user ID from question."""
        patterns = [
            r'user\s+(\d+)',
            r'userid\s+(\d+)',
            r'user\s+id\s+(\d+)',
            r'age\s+of\s+user\s+(\d+)',
            r'(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_location(self, question: str) -> str:
        """Extract location from question."""
        locations = ['moody center', 'downtown', 'university', 'airport', 'domain']
        
        for location in locations:
            if location in question.lower():
                return location.title()
        
        return "specified location"
    
    def save_system(self, filepath: str):
        """Save the RAG system to disk."""
        system_data = {
            'data_chunks': self.data_chunks,
            'embeddings': self.embeddings
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(system_data, f)
        
        print(f"✅ Saved RAG system to {filepath}")
    
    def load_system(self, filepath: str):
        """Load the RAG system from disk."""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                system_data = pickle.load(f)
            
            self.data_chunks = system_data['data_chunks']
            self.embeddings = system_data['embeddings']
            
            # Recreate FAISS index
            if self.embeddings is not None:
                dimension = self.embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)
                faiss.normalize_L2(self.embeddings)
                self.index.add(self.embeddings)
            
            print(f"✅ Loaded RAG system from {filepath}")
            return True
        
        return False

# Example usage
if __name__ == "__main__":
    rag = FetiiRAGSystem('FetiiAI_Data_Austin.xlsx')
    rag.load_and_process_data()
    rag.create_data_chunks()
    rag.create_embeddings()
    
    # Test queries
    test_queries = [
        "age of user 8794",
        "How many groups went to Moody Center?",
        "What are the top drop-off spots for 18-24 year-olds?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = rag.answer_question(query)
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.3f}")