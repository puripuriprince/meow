# 🚀 Quick Setup Guide

## 1. Get Cerebras API Key (Free!)

1. **Visit**: [https://cloud.cerebras.ai/](https://cloud.cerebras.ai/)
2. **Sign up** with email or Google account
3. **Go to**: Dashboard → API Keys
4. **Click**: "Create API Key"
5. **Copy** the key (starts with `csk-...`)

## 2. Add API Key to Environment

Edit `/backend/.env` and add:
```bash
CEREBRAS_API_KEY=csk-your-actual-key-here
```

## 3. Start the Server

```bash
npm run dev
```

## 4. Test Everything Works

```bash
# In the backend directory
node test-api.js
```

## 5. Try the CLI Example

```bash
# In the backend directory  
node cli-example.js
```

## 🎯 Your API Endpoints

- **Chat**: `POST http://localhost:3001/api/chat/completions`
- **Models**: `GET http://localhost:3001/api/chat/models`
- **Health**: `GET http://localhost:3001/health`

## 🔧 OpenAI Compatible Usage

Any CLI tool that works with OpenAI can now use your endpoint:

```python
import openai

openai.api_base = "http://localhost:3001/api/chat"
openai.api_key = "not-needed"

response = openai.ChatCompletion.create(
    model="llama3.1-8b",
    messages=[{"role": "user", "content": "What is XSS?"}]
)
```

## 💡 Features

- ✅ **OpenAI Compatible**: Drop-in replacement
- ✅ **Auto Context**: Injects your XSS knowledge automatically  
- ✅ **Free Cerebras**: No OpenAI costs
- ✅ **Local Control**: Runs on your machine
- ✅ **Custom Knowledge**: Edit `/src/context/system_context.md`

## 🆘 Troubleshooting

### "API Key Error"
- Make sure `.env` has `CEREBRAS_API_KEY=csk-...`
- Check your key is valid at [cloud.cerebras.ai](https://cloud.cerebras.ai)

### "Connection Refused"  
- Make sure server is running: `npm run dev`
- Check it's on port 3001: `http://localhost:3001/health`

### "No Context Loaded"
- Check `/src/context/system_context.md` exists
- Restart the server after editing context

---

🎉 **That's it!** Your OpenAI-compatible API with custom XSS knowledge is ready!
