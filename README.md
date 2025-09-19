# FetiiAI Chatbot - Hackathon Submission

## 🚗 Overview

This is an interactive GPT-powered chatbot that answers smart, real-world questions based on Fetii's rideshare data from Austin, TX. The chatbot can analyze trip patterns, demographic trends, and group movement data to provide insights about Fetii's service usage.

## 🎯 Features

- **Natural Language Queries**: Ask questions in plain English about Fetii's data
- **Smart Data Analysis**: Automatically categorizes locations, age groups, and trip patterns
- **Interactive Visualizations**: Charts and graphs to visualize data insights
- **Real-time Processing**: Instant analysis of complex queries
- **Comprehensive Coverage**: Handles trip data, rider demographics, and group patterns

## 📊 Data Analysis Capabilities

The chatbot can answer queries like:
- "How many groups went to Moody Center last month?"
- "What are the top drop-off spots for 18-24 year-olds on Saturday nights?"
- "When do large groups (6+ riders) typically ride downtown?"
- "Show me trip patterns for West Campus"
- "What's the age distribution of riders?"

## 🛠️ Technical Stack

- **Frontend**: Streamlit for interactive web interface
- **Data Processing**: Pandas for data manipulation and analysis
- **AI Integration**: OpenAI GPT-3.5-turbo for natural language responses
- **Visualization**: Plotly for interactive charts and graphs
- **Data Source**: Excel file with Fetii's Austin rideshare data

## 📁 Project Structure

```
hackathon/
├── FetiiAI_Data_Austin.xlsx     # Source data file
├── data_processor.py            # Data processing and analysis engine
├── fetii_chatbot.py            # Main chatbot with GPT integration
├── fetii_chatbot_demo.py       # Demo version (no API key required)
├── requirements.txt            # Python dependencies
├── env_example.txt            # Environment variables template
└── README.md                  # This file
```

## 🚀 Quick Start

### Option 1: Demo Version (No API Key Required)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo chatbot
streamlit run fetii_chatbot_demo.py
```

### Option 2: Full Version (With GPT Integration)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
# Copy env_example.txt to .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here

# Run the full chatbot
streamlit run fetii_chatbot.py
```

## 📈 Data Insights

The chatbot analyzes:
- **2,000 trips** from Austin, TX
- **11,903 rider records** with detailed trip information
- **7,276 users** with demographic data
- **Date range**: August 31 - September 8, 2025

### Key Findings:
- **Age Distribution**: 18-24 year olds dominate (9,052 riders)
- **Group Sizes**: Very large groups (8+ passengers) are most common
- **Top Locations**: Campus/University and Downtown are popular destinations
- **Peak Times**: Evening hours show highest activity

## 🎨 Features in Detail

### Smart Query Processing
- Automatically extracts locations, time periods, age groups, and group sizes
- Handles natural language variations and synonyms
- Provides contextual responses based on data availability

### Data Visualization
- Interactive bar charts for trip trends over time
- Pie charts for location distribution
- Histograms for group size analysis
- Real-time data filtering and aggregation

### Comprehensive Analysis
- **Location Analysis**: Categorizes addresses into meaningful groups (Campus, Downtown, Entertainment, etc.)
- **Demographic Insights**: Age group analysis with trip patterns
- **Temporal Patterns**: Time-based analysis (hour, day, week, month)
- **Group Dynamics**: Size-based trip analysis

## 🔧 Customization

The chatbot is designed to be easily extensible:
- Add new location categories in `data_processor.py`
- Extend query patterns in the chatbot's analysis methods
- Add new visualization types for different data insights
- Integrate additional data sources

## 📝 Submission Details

**What I Built:**
A comprehensive data analysis chatbot that transforms Fetii's rideshare data into actionable insights through natural language queries.

**How It Works:**
1. **Data Processing**: Cleans and categorizes raw trip data into structured insights
2. **Query Analysis**: Uses pattern matching and NLP techniques to understand user intent
3. **Data Retrieval**: Queries the processed dataset based on extracted parameters
4. **Response Generation**: Provides detailed insights with visualizations
5. **Interactive Interface**: Streamlit web app for seamless user experience

**Improvements for Next Version:**
- Enhanced NLP with more sophisticated query understanding
- Real-time data updates and live dashboard
- Advanced machine learning for predictive analytics
- Integration with Fetii's live API for real-time data
- Mobile-responsive design and mobile app
- Voice interface for hands-free querying
- Advanced filtering and drill-down capabilities

## 🏆 Hackathon Goals Achieved

✅ **Interactive GPT-powered chatbot** - Built with OpenAI integration
✅ **Smart, real-world questions** - Handles complex analytical queries
✅ **Fetii rideshare data integration** - Comprehensive data processing
✅ **Testable demo** - Works without setup or installation
✅ **Real insights** - Provides meaningful analysis of trip patterns

## 🎯 Demo Access

The chatbot is ready to demo and can be accessed by running the Streamlit application. It provides immediate insights into Fetii's Austin operations and can answer complex questions about user behavior, trip patterns, and demographic trends.

---

**Built for the FetiiAI Hackathon** 🚗💨
*Transforming rideshare data into intelligent insights*