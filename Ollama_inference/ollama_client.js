async function sendMessage() {
    // const message = userInput.value.trim();
    const message = "hello"
    if (!message) return;

    // Add user message to chat
    console.log('You: ' + message, 'user-message');
    // userInput.value = '';

    try {
      const response = await fetch('http://127.0.0.1:11434/v1/chat/completions', {  // Updated endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer aaaaaaaa`
        },
        body: JSON.stringify({
          model: "gemma2:latest",  // Change this to your preferred model
          messages: [{ role: "user", content: message }],  // Updated message structure
          stream: false
        })
      });

      const data = await response.json();
      console.log('Bot: ' + data.choices[0].message.content, 'bot-message');  // Updated response handling
    } catch (error) {
      console.log('Error: Could not connect to Ollama. Make sure it\'s running on localhost:11434', 'error-message');
      console.error('Error:', error);
    }
  }


  await sendMessage()
