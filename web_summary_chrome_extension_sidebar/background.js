// Service worker for background tasks
chrome.runtime.onInstalled.addListener(() => {
    // Initialize extension settings
    chrome.storage.local.set({
        summaryLength: 'medium'
    });
});

// Handle messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Add any background processing logic here
    return true;
});

// Add side panel behavior
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));

// Enable side panel for all tabs
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    chrome.sidePanel.setOptions({
      tabId,
      path: 'sidebar.html',
      enabled: true
    });
  }
});
