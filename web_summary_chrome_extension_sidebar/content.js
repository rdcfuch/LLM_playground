// This file handles content script functionality
// It will be injected into web pages as specified in manifest.json

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getContent") {
        const content = document.body.innerText;
        sendResponse({ content: content });
    }
});
