// Configuration
const CONFIG = {
  API_ENDPOINT: 'https://api.deepseek.com/v1/chat/completions',
  MODEL: 'deepseek-chat',
  SYSTEM_PROMPT: 'You are a translator. Translate the following text to Chinese. Only respond with the translation, no explanations.',
  TEMPERATURE: 0.3
};

// Store API key in extension storage
let openaiApiKey = 'sk-be34b6c3d96f416b86a097987ac9b1fe';

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "detectLanguage") {
    chrome.tabs.detectLanguage(sender.tab.id, (language) => {
      sendResponse({ language: language });
    });
    return true; // Will respond asynchronously
  }
  
  if (request.action === "translate") {
    if (!openaiApiKey) {
      sendResponse({ error: "API key not set" });
      return false;
    }
    
    translateWithDeepseek(request.text)
      .then(translation => sendResponse({ translation }))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Will respond asynchronously
  }
  
  if (request.action === "setApiKey") {
    openaiApiKey = request.apiKey;
    // Store in chrome.storage for persistence
    chrome.storage.local.set({ openaiApiKey: request.apiKey }, () => {
      sendResponse({ success: true });
    });
    return true;
  }
});

// Load API key when extension starts
chrome.storage.local.get(['openaiApiKey'], (result) => {
  if (result.openaiApiKey) {
    openaiApiKey = result.openaiApiKey;
  }
});

async function translateWithDeepseek(text) {
  try {
    console.log('Sending request to Deepseek:', {
      url: CONFIG.API_ENDPOINT,
      model: CONFIG.MODEL,
      text: text
    });

    const response = await fetch(CONFIG.API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openaiApiKey}`
      },
      body: JSON.stringify({
        model: CONFIG.MODEL,
        messages: [
          {
            role: "system",
            content: CONFIG.SYSTEM_PROMPT
          },
          {
            role: "user",
            content: text
          }
        ],
        temperature: CONFIG.TEMPERATURE
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Deepseek API error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      throw new Error(`Translation request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Deepseek response:', data);
    
    if (data && data.choices && data.choices[0] && data.choices[0].message) {
      return data.choices[0].message.content.trim();
    } else {
      throw new Error('Invalid response format from Deepseek');
    }
  } catch (error) {
    console.error('Translation error:', error);
    throw error;
  }
}
