// Service worker for background tasks
chrome.runtime.onInstalled.addListener(() => {
    // Initialize extension settings
    chrome.storage.local.set({
        summaryLength: 'medium'
    });
});

// Set up side panel behavior
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

// Handle messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'openSidebar') {
        // Store the tab ID for the sidebar to use
        chrome.storage.local.set({ 'pendingSummarizeTabId': sender.tab.id }, () => {
            // Open the sidebar
            chrome.sidePanel.open({ tabId: sender.tab.id });
        });
    }
    return true;
});
