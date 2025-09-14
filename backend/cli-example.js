#!/usr/bin/env node

// Example CLI tool that uses the EvoSec API like OpenAI
const axios = require('axios');
const readline = require('readline');

const API_BASE = 'http://localhost:3001/api/chat';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔒 EvoSec AI Assistant');
console.log('Ask me anything about cybersecurity!\n');

async function askQuestion(question) {
  try {
    const response = await axios.post(`${API_BASE}/completions`, {
      model: 'llama3.1-8b',
      messages: [
        {
          role: 'user',
          content: question
        }
      ],
      temperature: 0.7,
      max_tokens: 500
    });

    return response.data.choices[0].message.content;
  } catch (error) {
    if (error.response) {
      throw new Error(`API Error: ${error.response.data.error?.message || 'Unknown error'}`);
    } else {
      throw new Error(`Network Error: ${error.message}`);
    }
  }
}

function promptUser() {
  rl.question('You: ', async (question) => {
    if (question.toLowerCase() === 'exit' || question.toLowerCase() === 'quit') {
      console.log('👋 Goodbye!');
      rl.close();
      return;
    }

    if (!question.trim()) {
      promptUser();
      return;
    }

    try {
      console.log('\n🤖 EvoSec AI: Thinking...');
      const answer = await askQuestion(question);
      console.log('\n🤖 EvoSec AI:', answer);
      console.log('\n' + '-'.repeat(50) + '\n');
    } catch (error) {
      console.error('\n❌ Error:', error.message);
      console.log('\n' + '-'.repeat(50) + '\n');
    }

    promptUser();
  });
}

// Start the CLI
promptUser();
