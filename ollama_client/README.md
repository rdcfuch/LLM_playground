# Ollama Chat Frontend

A beautiful, Material Design-inspired web frontend for your local Ollama server. This chat interface provides a ChatGPT-like experience with markdown rendering, no build tools required!

## Features

- 🎨 **Material Design UI** - Clean, modern interface inspired by Google's Material Design
- 💬 **ChatGPT-like Experience** - Familiar chat interface with message bubbles and avatars
- 📝 **Markdown Support** - Full markdown rendering for code blocks, lists, headers, and more
- ⚙️ **Configurable Settings** - Adjust server URL, model, and temperature
- 📱 **Responsive Design** - Works great on desktop, tablet, and mobile devices
- 🔒 **No Build Required** - Pure HTML/CSS/JavaScript, runs directly in browser
- 💾 **Local Storage** - Settings and preferences are saved locally

## Prerequisites

1. **Ollama Server**: Make sure you have Ollama installed and running on your machine
   - Install from: https://ollama.ai
   - **Important**: Start the server with CORS enabled: `OLLAMA_ORIGINS=* ollama serve`
   - Pull a model: `ollama pull qwen3:8b` (or any other model you prefer)

2. **Web Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge)

## Setup

1. Make sure you have Ollama installed and running on your system

2. **Important**: Start Ollama with CORS enabled for web browser access:
   ```bash
   OLLAMA_ORIGINS=* ollama serve
   ```
   
   Or on Windows:
   ```cmd
   set OLLAMA_ORIGINS=*
   ollama serve
   ```

3. Pull a model (if you haven't already):
   ```bash
   ollama pull qwen3:8b
   # or any other model you prefer
   ```

4. Serve the frontend using a local HTTP server:
   ```bash
   python3 -m http.server 8080
   ```
   Then visit `http://localhost:8080`

## Quick Start

1. **Clone or Download** this repository to your local machine

2. **Open the Frontend**: Serve it with an HTTP server (recommended)
   - See Setup section above for server instructions
   - Or double-click `index.html` (may have CORS issues)

3. **Configure Settings** (if needed):
   - Click the settings icon (⚙️) in the top-right corner
   - Adjust the Ollama server URL (default: `http://localhost:11434`)
   - Select your preferred model
   - Adjust temperature for response creativity

4. **Start Chatting**: Type your message and press Enter or click Send!

## Troubleshooting

### "Cannot connect to Ollama server" Error

This error typically occurs due to CORS restrictions. Make sure you:

1. **Start Ollama with CORS enabled**:
   ```bash
   OLLAMA_ORIGINS=* ollama serve
   ```

2. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Check if your model exists**:
   ```bash
   ollama list
   ```

4. **Update the model in settings** if needed (click the settings gear icon)

### Alternative: Use Ollama with Docker

If you're using Docker, run Ollama with CORS enabled:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 -e OLLAMA_ORIGINS=* --name ollama ollama/ollama
```

## Serving with HTTP Server (Recommended)

While the frontend works by opening the HTML file directly, serving it through an HTTP server is recommended to avoid CORS issues:

### Using Python (if available):
```bash
cd /path/to/ollama_client
python3 -m http.server 8080
```
Then open: http://localhost:8080

### Using any other simple server:
- If you have Node.js: `npx serve .`
- If you have PHP: `php -S localhost:8080`
- Or use any other local server solution

## Configuration

### Settings Panel
Access the settings by clicking the gear icon (⚙️):

- **Server URL**: Your Ollama server endpoint (default: http://localhost:11434)
- **Model**: Select from available models (llama2, llama3, mistral, codellama, etc.)
- **Temperature**: Control response creativity (0.0 = focused, 1.0 = creative)

### Supported Models
The interface supports any model available in your Ollama installation. Common models include:
- `llama2` - Meta's Llama 2 model
- `llama3` - Meta's Llama 3 model
- `mistral` - Mistral AI's model
- `codellama` - Code-specialized Llama model
- `phi` - Microsoft's Phi model
- And many more!

To see available models: `ollama list`

## Features in Detail

### Markdown Rendering
The assistant's responses support full markdown formatting:
- **Headers** (# ## ###)
- **Bold** and *italic* text
- `Inline code` and code blocks
- Lists (bulleted and numbered)
- Blockquotes
- Links
- And more!

### Responsive Design
The interface adapts to different screen sizes:
- Desktop: Full-width layout with sidebar settings
- Tablet: Optimized spacing and touch targets
- Mobile: Compact layout with full-screen settings panel

### Chat History
The application maintains conversation context by sending recent message history to the model, enabling coherent multi-turn conversations.

## Troubleshooting

### Common Issues

1. **"Connection Error" or "No response"**
   - Ensure Ollama is running: `ollama serve`
   - Check the server URL in settings
   - Verify the model is installed: `ollama list`

2. **CORS Errors**
   - Serve the frontend through an HTTP server instead of opening the file directly
   - Ensure Ollama allows cross-origin requests

3. **Model Not Found**
   - Install the model: `ollama pull <model-name>`
   - Check available models: `ollama list`
   - Update the model name in settings

4. **Slow Responses**
   - This is normal for large models on slower hardware
   - Try a smaller model like `phi` or `mistral`
   - Reduce the temperature setting

### Browser Compatibility
- Chrome/Chromium: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Edge: ✅ Full support
- Internet Explorer: ❌ Not supported

## Customization

The frontend is built with vanilla HTML/CSS/JavaScript, making it easy to customize:

- **Styling**: Modify `styles.css` to change colors, fonts, or layout
- **Functionality**: Edit `script.js` to add new features or modify behavior
- **Models**: Add more models to the dropdown in `index.html`

## Security Notes

- The frontend uses DOMPurify to sanitize markdown content
- Settings are stored in browser's localStorage
- No data is sent to external servers (everything stays local)
- HTTPS is recommended if serving over a network

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this frontend!

## License

This project is open source and available under the MIT License.

---

**Enjoy chatting with your local AI models!** 🤖✨