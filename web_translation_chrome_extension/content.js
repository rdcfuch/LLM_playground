// Create and inject floating button
function createFloatingButton() {
  // Check if button already exists
  if (document.getElementById('translate-button')) {
    return;
  }

  const button = document.createElement('button');
  button.id = 'translate-button';
  const img = document.createElement('img');
  img.src = chrome.runtime.getURL('images/translation.svg');
  img.style.width = '24px';
  img.style.height = '24px';
  button.appendChild(img);
  button.style.position = 'fixed';
  button.style.top = '20px';
  button.style.right = '20px';
  button.style.zIndex = '10000';
  button.style.padding = '10px';
  button.style.width = '44px';
  button.style.height = '44px';
  button.style.backgroundColor = '#4CAF50';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '50%';
  button.style.display = 'flex';
  button.style.alignItems = 'center';
  button.style.justifyContent = 'center';
  button.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
  button.style.transition = 'all 0.3s ease';

  document.body.appendChild(button);

  // Add drag functionality
  let isDragging = false;
  let startX, startY, startTop, startRight;
  let hasMoved = false;
  const moveThreshold = 5; // pixels

  function handleMouseDown(e) {
    if (button.disabled) return;
    
    isDragging = true;
    hasMoved = false;
    const rect = button.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    startTop = rect.top;
    startRight = window.innerWidth - rect.right;
    
    e.preventDefault();
  }

  function handleMouseMove(e) {
    if (!isDragging) return;

    const deltaX = e.clientX - startX;
    const deltaY = e.clientY - startY;

    // Check if movement is greater than threshold
    if (!hasMoved && (Math.abs(deltaX) > moveThreshold || Math.abs(deltaY) > moveThreshold)) {
      hasMoved = true;
    }

    const newTop = startTop + deltaY;
    const newRight = startRight - deltaX;

    // Keep button within viewport bounds
    const maxTop = window.innerHeight - button.offsetHeight;
    button.style.top = Math.min(Math.max(0, newTop), maxTop) + 'px';
    button.style.right = Math.min(Math.max(0, newRight), window.innerWidth - button.offsetWidth) + 'px';
  }

  function handleMouseUp() {
    isDragging = false;
  }

  button.addEventListener('mousedown', handleMouseDown);
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);

  // Separate click handler for translation
  button.addEventListener('click', (e) => {
    if (!hasMoved) {
      handleTranslation();
    }
  });
}

// Handle translation process
async function handleTranslation() {
  const button = document.getElementById('translate-button');
  if (button.disabled) return; // Prevent any translation if already in progress
  
  // Set translation in progress state
  button.disabled = true;
  const img = button.querySelector('img');
  img.style.opacity = '0.5';
  button.style.backgroundColor = '#FFA726'; // Orange color for ongoing state
  button.style.cursor = 'not-allowed';
  
  // Add loading animation
  button.style.animation = 'pulse 1.5s infinite';
  const style = document.createElement('style');
  style.textContent = `
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
  `;
  document.head.appendChild(style);

  try {
    // Select all paragraphs and lists that haven't been translated
    const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, ul, ol');
    const untranslatedElements = Array.from(elements).filter(el => 
      !el.nextElementSibling?.classList.contains('translation') &&
      el.textContent.trim() &&
      !el.closest('script') &&
      !el.closest('style') &&
      !el.closest('button') &&  // Exclude buttons
      !el.matches('#translate-button, #translate-button *') // Exclude our translation button specifically
    );

    // Process elements in batches
    const batchSize = 5;
    for (let i = 0; i < untranslatedElements.length; i += batchSize) {
      const batch = untranslatedElements.slice(i, i + batchSize);
      await Promise.all(batch.map(async (element) => {
        // Clone the element to work with its content
        const tempElement = element.cloneNode(true);
        
        // Remove buttons and links from the clone
        tempElement.querySelectorAll('button, a').forEach(el => el.remove());
        
        // Get text and preserve numbers and links as placeholders
        let text = tempElement.textContent.trim();
        const numbers = [];
        const links = [];
        
        // Replace numbers with placeholders
        text = text.replace(/\d+(\.\d+)?/g, (match) => {
          numbers.push(match);
          return `[NUM${numbers.length - 1}]`;
        });
        
        // Replace links with placeholders
        element.querySelectorAll('a').forEach((link, index) => {
          const linkText = link.textContent.trim();
          if (linkText) {
            links.push(linkText);
            text = text.replace(linkText, `[LINK${index}]`);
          }
        });

        if (text && !/^[\d\s]*$/.test(text)) { // Only translate if there's non-numeric content
          const response = await chrome.runtime.sendMessage({
            action: "translate",
            text: text
          });

          if (response.error) {
            if (response.error === "API key not set") {
              const apiKey = prompt("Please enter your OpenAI API key:");
              if (apiKey) {
                await chrome.runtime.sendMessage({
                  action: "setApiKey",
                  apiKey: apiKey
                });
                // Retry translation with new API key
                response = await chrome.runtime.sendMessage({
                  action: "translate",
                  text: text
                });
              } else {
                throw new Error("API key is required for translation");
              }
            } else {
              throw new Error(response.error);
            }
          }

          // Restore numbers and links in the translation
          let translatedText = response.translation;
          numbers.forEach((num, i) => {
            translatedText = translatedText.replace(`[NUM${i}]`, num);
          });
          links.forEach((link, i) => {
            translatedText = translatedText.replace(`[LINK${i}]`, link);
          });

          // Create translation element with the same tag type
          const translationElement = document.createElement(element.tagName);
          translationElement.classList.add('translation');
          translationElement.textContent = translatedText;
          translationElement.style.color = '#666';
          translationElement.style.backgroundColor = '#f5f5f5';
          translationElement.style.padding = '10px';
          translationElement.style.margin = '5px 0';
          translationElement.style.borderLeft = '3px solid #4CAF50';
          translationElement.style.fontFamily = '"Microsoft YaHei", "微软雅黑", sans-serif';
          translationElement.style.fontWeight = 'bold';
          
          // Insert after the original element
          element.insertAdjacentElement('afterend', translationElement);
        }
      }));
    }
  } catch (error) {
    console.error('Translation error:', error);
    alert(error.message || 'Translation failed. Please try again.');
  } finally {
    // Reset button state
    button.disabled = false;
    const img = button.querySelector('img');
    img.style.opacity = '1';
    button.style.backgroundColor = '#4CAF50';
    button.style.cursor = '';
    button.style.animation = 'none';
    style.remove(); // Remove the animation style
  }
}

// Initialize button
// Run immediately and also after DOM content loaded to ensure it works in all cases
createFloatingButton();
document.addEventListener('DOMContentLoaded', createFloatingButton);
// Also handle dynamic page loads (SPAs)
window.addEventListener('load', createFloatingButton);
