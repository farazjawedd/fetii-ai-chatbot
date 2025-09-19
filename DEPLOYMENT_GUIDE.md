# 🚀 FetiiAI Chatbot - Deployment Guide

## Option 1: Streamlit Cloud (Recommended)

### Step 1: Push to GitHub
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial FetiiAI chatbot submission"

# Create GitHub repository and push
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fetii-ai-chatbot.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/fetii-ai-chatbot`
5. Set main file path: `streamlit_app.py`
6. Add environment variable: `GEMINI_API_KEY` = `AIzaSyDLB8NYTk_pSpWWXIgpEhXt-hoHTfVrC3E`
7. Click "Deploy"

### Step 3: Access Your App
Your chatbot will be available at: `https://YOUR_APP_NAME.streamlit.app`

## Option 2: Vercel Deployment

### Step 1: Prepare for Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login
```

### Step 2: Deploy
```bash
# Deploy to Vercel
vercel

# Set environment variable
vercel env add GEMINI_API_KEY
# Enter: AIzaSyDLB8NYTk_pSpWWXIgpEhXt-hoHTfVrC3E
```

## Option 3: Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## 🎯 What You'll Get

### ✅ **Live Demo URL**
- Accessible from anywhere
- No setup required for users
- Mobile responsive

### ✅ **Full Functionality**
- GPT-powered responses (with Gemini API)
- Interactive data visualizations
- Real-time query processing
- All hackathon requirements met

### ✅ **Professional Presentation**
- Clean, modern interface
- Example queries ready to test
- Data insights and visualizations
- Ready for judges to demo

## 📊 Test Queries for Demo

1. **"How many groups went to Moody Center last month?"**
   - Expected: 6 trips found

2. **"What are the top drop-off spots for 18-24 year-olds on Saturday nights?"**
   - Expected: Downtown (834), Other (1141), Campus (201)

3. **"When do large groups (6+ riders) typically ride downtown?"**
   - Expected: Peak at 22:00 (157 trips), 23:00 (140 trips)

## 🔧 Environment Variables

For the full GPT experience, set:
- `GEMINI_API_KEY`: `AIzaSyDLB8NYTk_pSpWWXIgpEhXt-hoHTfVrC3E`

## 📱 Features

- **Smart Query Processing**: Understands natural language
- **Data Visualizations**: Interactive charts and graphs
- **Real-time Analysis**: Instant insights from 2,000+ trips
- **Mobile Responsive**: Works on all devices
- **Professional UI**: Clean, modern design

## 🏆 Ready for Submission

Your chatbot is now ready for the FetiiAI Hackathon submission! It demonstrates:
- ✅ Interactive GPT-powered chatbot
- ✅ Smart, real-world questions answered
- ✅ Fetii rideshare data integration
- ✅ Testable without setup
- ✅ Real insights and visualizations

**Demo URL**: Ready to share with judges
**Code**: Clean, well-documented, production-ready
**Documentation**: Complete setup and deployment guides

---

**Let's win this hackathon!** 🚗💨🏆