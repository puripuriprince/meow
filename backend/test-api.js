#!/usr/bin/env node

// Simple test script to verify the chat API is working
const axios = require('axios');

const API_BASE = 'http://localhost:3001';

async function testChatAPI() {
  console.log('🧪 Testing EvoSec Chat API...\n');

  try {
    // Test 1: Health check
    console.log('1️⃣ Testing health endpoint...');
    const healthResponse = await axios.get(`${API_BASE}/health`);
    console.log('✅ Health check passed:', healthResponse.data.message);

    // Test 2: Models endpoint
    console.log('\n2️⃣ Testing models endpoint...');
    const modelsResponse = await axios.get(`${API_BASE}/api/chat/models`);
    console.log('✅ Models endpoint working. Available models:', 
      modelsResponse.data.data.map(m => m.id).join(', '));

    // Test 3: Chat completions
    console.log('\n3️⃣ Testing chat completions...');
    const chatRequest = {
      model: 'llama3.1-8b',
      messages: [
        {
          role: 'user',
          content: 'What is XSS? Give me a brief explanation.'
        }
      ],
      temperature: 0.7,
      max_tokens: 200
    };

    console.log('Sending request:', JSON.stringify(chatRequest, null, 2));
    
    const startTime = Date.now();
    const chatResponse = await axios.post(`${API_BASE}/api/chat/completions`, chatRequest);
    const endTime = Date.now();
    
    console.log('✅ Chat completion successful!');
    console.log(`⏱️ Response time: ${endTime - startTime}ms`);
    console.log(`📊 Usage: ${chatResponse.data.usage.total_tokens} tokens`);
    console.log('\n📝 AI Response:');
    console.log('=' .repeat(50));
    console.log(chatResponse.data.choices[0].message.content);
    console.log('=' .repeat(50));

    console.log('\n🎉 All tests passed! Your API is working correctly.');
    
  } catch (error) {
    console.error('\n❌ Test failed:');
    
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Error:', JSON.stringify(error.response.data, null, 2));
      
      if (error.response.status === 401 || error.response.status === 403) {
        console.error('\n💡 This looks like an API key issue. Make sure:');
        console.error('   1. You have CEREBRAS_API_KEY set in /backend/.env');
        console.error('   2. Your API key is valid and starts with "csk-"');
        console.error('   3. You have credits available in your Cerebras account');
      }
    } else if (error.code === 'ECONNREFUSED') {
      console.error('\n💡 Server not running. Start it with: npm run dev');
    } else {
      console.error('Error:', error.message);
    }
  }
}

// Run the test
testChatAPI();
