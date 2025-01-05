// This file handles content script functionality
// It will be injected into web pages as specified in manifest.json

// Function to get page content
function getPageContent() {
    // Get the article content if available
    const article = document.querySelector('article');
    if (article) {
        return article.innerText;
    }

    // Get the main content if available
    const main = document.querySelector('main');
    if (main) {
        return main.innerText;
    }

    // Otherwise, get all paragraph text
    const paragraphs = Array.from(document.getElementsByTagName('p'));
    return paragraphs.map(p => p.innerText).join('\n\n');
}

// Handle content script message
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getContent') {
        const content = getPageContent();
        sendResponse({ content: content });
    }
});

// Create and inject floating button
function createFloatingButton() {
    // Check if button already exists
    if (document.getElementById('summary-fab')) {
        return;
    }

    const button = document.createElement('div');
    button.id = 'summary-fab';
    button.innerHTML = `
        <div class="fab-icon">
            <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24">
                <path d="M0 0h24v24H0z" fill="none"/>
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
            </svg>
        </div>
    `;
    
    // Add styles for the floating button
    const style = document.createElement('style');
    style.textContent = `
        #summary-fab {
            position: fixed;
            right: 20px;
            bottom: 20px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background-color: #E91E63;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, box-shadow 0.2s;
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        #summary-fab:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }
        
        #summary-fab .fab-icon {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #summary-fab svg {
            width: 24px;
            height: 24px;
            fill: white;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(button);
    
    // Add click handler
    button.addEventListener('click', () => {
        chrome.runtime.sendMessage({ action: 'openSidebar' });
    });
}

// Initialize floating button when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createFloatingButton);
} else {
    createFloatingButton();
}

// Re-add the button if the page content changes significantly
const observer = new MutationObserver((mutations) => {
    if (!document.getElementById('summary-fab')) {
        createFloatingButton();
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
