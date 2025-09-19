# FetiiAI Chatbot - Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial FetiiAI chatbot submission"
   git branch -M main
   git remote add origin https://github.com/yourusername/fetii-ai-chatbot.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `fetii_chatbot_demo.py`
   - Click "Deploy"

3. **For GPT Version** (with API key):
   - Use `fetii_chatbot.py` as main file
   - Add environment variable: `OPENAI_API_KEY`
   - Set your OpenAI API key in the Streamlit Cloud settings

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo version (no API key needed)
streamlit run fetii_chatbot_demo.py

# Run full version (requires OpenAI API key)
# First, create .env file with your API key
streamlit run fetii_chatbot.py
```

### Option 3: Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "fetii_chatbot_demo.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t fetii-chatbot .
docker run -p 8501:8501 fetii-chatbot
```

## 📋 Pre-deployment Checklist

- [ ] All files are in the repository
- [ ] `requirements.txt` includes all dependencies
- [ ] Data file `FetiiAI_Data_Austin.xlsx` is included
- [ ] Demo version works without API keys
- [ ] Tests pass (`python test_queries.py`)
- [ ] README.md is complete
- [ ] Environment variables are documented

## 🔧 Environment Variables

For the full GPT version, you'll need:
- `OPENAI_API_KEY`: Your OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)

## 📱 Mobile Responsiveness

The Streamlit app is mobile-responsive and works on:
- Desktop browsers
- Tablet devices
- Mobile phones
- Touch interfaces

## 🎯 Demo URLs

Once deployed, your chatbot will be available at:
- **Streamlit Cloud**: `https://your-app-name.streamlit.app`
- **Local**: `http://localhost:8501`

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Data File Not Found**: Ensure `FetiiAI_Data_Austin.xlsx` is in the root directory
3. **API Key Issues**: Check that your OpenAI API key is valid and has credits
4. **Memory Issues**: The app processes 11K+ records, ensure sufficient memory

### Performance Tips:

- The demo version loads faster (no API calls)
- Data processing happens once on startup
- Caching is built into Streamlit for better performance

## 📊 Monitoring

Monitor your deployment:
- **Streamlit Cloud**: Built-in analytics dashboard
- **Local**: Check terminal output for errors
- **Docker**: Use `docker logs <container_id>`

## 🔄 Updates

To update your deployment:
1. Make changes to your code
2. Commit and push to GitHub
3. Streamlit Cloud auto-deploys on push
4. For local: restart the Streamlit server

---

**Ready to deploy!** 🚀