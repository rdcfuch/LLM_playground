# Web Translation Chrome Extension

A Chrome extension that adds Chinese translations under webpage content.

## Features

- Green floating translation button
- Automatic language detection
- Inline Chinese translations for webpage content
- Clean and minimal UI

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select this extension directory

## Usage

1. Click the extension icon to see instructions
2. Click the green floating button on any webpage to translate content
3. Chinese translations will appear under the original text

## Note

This is a basic implementation. To make it fully functional, you'll need to:
1. Replace the mock translation function in content.js with an actual translation API
2. Add error handling for API calls
3. Consider rate limiting and optimization for large pages

## Permissions

- activeTab: Required for accessing current page content
- tabs: Required for language detection
- scripting: Required for injecting translation content
