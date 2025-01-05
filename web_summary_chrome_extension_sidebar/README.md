# Web Page Summarizer Chrome Extension

A Chrome extension that uses AI to summarize web pages and allows users to ask follow-up questions about the content.

## Features

- Automatic summarization of web page content
- Adjustable summary length (short, medium, long)
- Follow-up questions capability
- Local storage for user preferences
- Clean and intuitive user interface

## Installation

1. Clone this repository or download the files
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the extension directory

## Usage

1. Click the extension icon in your Chrome toolbar
2. Select your desired summary length
3. Click "Summarize" to generate a summary of the current page
4. Use the follow-up questions feature to ask specific questions about the content

## Development

To modify the extension:

1. Update the AI integration in `popup.js` with your preferred AI service
2. Test changes by reloading the extension in `chrome://extensions/`
3. Use Chrome DevTools to debug (right-click extension popup > Inspect)

## File Structure

- `manifest.json`: Extension configuration
- `popup.html`: Main extension interface
- `popup.js`: Main functionality
- `styles.css`: UI styling
- `content.js`: Content script for web page interaction
- `background.js`: Background service worker
- `images/`: Extension icons

## Note

This extension requires implementation of actual AI service integration for summarization and question-answering functionality. The current version includes placeholder functions that need to be connected to an AI API of your choice.
