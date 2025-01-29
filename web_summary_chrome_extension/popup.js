// DeepSeek API Configuration
const DeepSeek_MODEL = "deepseek-chat";
const DeepSeek_BASE_URL = "https://api.deepseek.com";
const DeepSeek_API_KEY = "sk-1577baabe3574262b21c2e2f249ac597";

document.addEventListener('DOMContentLoaded', () => {
    const summarizeButton = document.getElementById('summarize');
    const askQuestionButton = document.getElementById('ask-question');
    const lengthSelect = document.getElementById('length');
    const summaryElement = document.getElementById('summary');
    const loadingElement = document.getElementById('loading');
    const questionsSection = document.getElementById('questions-section');
    const questionInput = document.getElementById('question-input');
    const answerContainer = document.getElementById('answer-container');
    const suggestedQuestionsContainer = document.querySelector('.suggested-questions');

    // Load saved preferences
    chrome.storage.local.get(['summaryLength'], (result) => {
        if (result.summaryLength) {
            lengthSelect.value = result.summaryLength;
        }
    });

    // Save preferences when changed
    lengthSelect.addEventListener('change', () => {
        chrome.storage.local.set({
            summaryLength: lengthSelect.value
        });
    });

    // Set default language to Chinese if not set
    chrome.storage.local.get(['summaryLanguage'], (result) => {
        if (!result.summaryLanguage) {
            chrome.storage.local.set({ 'summaryLanguage': 'chinese' });
        }
        // Update the language selector to match storage
        const languageSelect = document.getElementById('language');
        languageSelect.value = result.summaryLanguage || 'chinese';
    });

    // Set default length to medium and store preference
    chrome.storage.local.get(['summaryLength'], (result) => {
        if (!result.summaryLength) {
            chrome.storage.local.set({ 'summaryLength': 'medium' });
        }
        // Update the length selector to match storage
        const lengthSelect = document.getElementById('length');
        lengthSelect.value = result.summaryLength || 'medium';
    });

    async function generateSuggestedQuestions(summary) {
        const prompt = `基于这段总结，生成3个最重要的后续问题。请用中文回答，以JSON数组格式返回。示例：["问题1？", "问题2？", "问题3？"]。问题应该简洁且有针对性：\n\n${summary}`;

        const apiKey = await getApiKey();
        return await fetchWithRetry(`${DeepSeek_BASE_URL}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: DeepSeek_MODEL,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                max_tokens: 200,
                temperature: 0.7
            })
        });
    }

    function displaySuggestedQuestions(questions) {
        suggestedQuestionsContainer.innerHTML = '';
        
        // Add title
        const titleDiv = document.createElement('div');
        titleDiv.className = 'suggested-questions-title';
        titleDiv.textContent = 'Follow-up Questions:';
        suggestedQuestionsContainer.appendChild(titleDiv);
        
        // Add questions
        questions.forEach(question => {
            const button = document.createElement('button');
            button.className = 'suggested-question';
            button.textContent = question;
            button.addEventListener('click', () => {
                questionInput.value = question;
                askQuestion(question);
            });
            suggestedQuestionsContainer.appendChild(button);
        });
        suggestedQuestionsContainer.classList.remove('hidden');
    }

    async function askQuestion(question) {
        try {
            const result = await chrome.storage.local.get(['currentSummary']);
            if (!result.currentSummary) {
                throw new Error('Please generate a summary first');
            }

            const apiKey = await getApiKey();
            const answer = await generateAnswer(question, result.currentSummary, apiKey);
            
            displayAnswer(answer);
        } catch (error) {
            answerContainer.textContent = 'Error: ' + error.message;
        }
    }

    summarizeButton.addEventListener('click', async () => {
        loadingElement.classList.remove('hidden');
        summaryElement.classList.add('hidden');
        suggestedQuestionsContainer.classList.add('hidden');
        questionsSection.classList.add('hidden');

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            const result = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: getPageContent
            });

            const pageContent = result[0].result;
            const apiKey = await getApiKey();
            const summary = await generateSummary(pageContent, lengthSelect.value, apiKey);
            
            displaySummary(summary);
            questionsSection.classList.remove('hidden');
            
            // Generate and display suggested questions
            const questions = await generateSuggestedQuestions(summary);
            displaySuggestedQuestions(questions);
            
            // Store the summary for follow-up questions
            chrome.storage.local.set({
                currentSummary: summary
            });
        } catch (error) {
            summaryElement.textContent = 'Error generating summary: ' + error.message;
            summaryElement.classList.remove('hidden');
        } finally {
            loadingElement.classList.add('hidden');
        }
    });

    askQuestionButton.addEventListener('click', () => {
        const question = questionInput.value.trim();
        if (!question) return;
        askQuestion(question);
    });
});

// Function to get page content
function getPageContent() {
    // Remove unnecessary elements
    const elementsToRemove = document.querySelectorAll('script, style, nav, footer, header, aside, iframe, img');
    elementsToRemove.forEach(element => element.remove());

    // Get main content
    const mainContent = document.body.innerText;
    return mainContent.trim();
}

// Function to generate summary using DeepSeek
async function generateSummary(content, length, apiKey) {
    let lengthPrompt;
    switch (length) {
        case 'short':
            lengthPrompt = 'concise (about 100 words)';
            break;
        case 'medium':
            lengthPrompt = 'moderate length (about 200 words)';
            break;
        case 'long':
            lengthPrompt = 'detailed (about 400 words)';
            break;
        default:
            lengthPrompt = 'moderate length (about 200 words)';
    }

    const prompt = `Please provide a ${lengthPrompt} summary of the following webpage content. Return the response in HTML format with the following structure:

<div class="summary-section">
    <h2>Summary: [Title]</h2>
    <div class="overview">[Overview paragraph with <strong>important terms</strong> highlighted]</div>
    
    <h3>Key Points:</h3>
    <ul>
        <li>[Point 1 with <strong>key terms</strong> highlighted]</li>
        <li>[Point 2 with <strong>key terms</strong> highlighted]</li>
        <li>[Point 3 with <strong>key terms</strong> highlighted]</li>
    </ul>
    
    <div class="important-terms">
        <h3>Important Terms:</h3>
        <ul>
            <li><strong>[Term 1]</strong>: [Brief description]</li>
            <li><strong>[Term 2]</strong>: [Brief description]</li>
        </ul>
    </div>
</div>

Content to summarize:

${content}`;

    try {
        const response = await fetch(`${DeepSeek_BASE_URL}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: DeepSeek_MODEL,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                max_tokens: 500,
                temperature: 0.7
            })
        });
        const data = await response.json();
        return data.choices[0].message.content;
    } catch (error) {
        throw new Error(`API request failed: ${error.message}`);
    }
}

// Function to generate answer using DeepSeek
async function generateAnswer(question, summary, apiKey) {
    const prompt = `Based on this summary:

${summary}

Please answer this question: "${question}"

Return the response in HTML format with the following structure:

<div class="answer-section">
    <div class="main-answer">[Main answer with <strong>important terms</strong> highlighted]</div>
    
    <h3>Supporting Points:</h3>
    <ul>
        <li>[Point 1 with <strong>key terms</strong> highlighted]</li>
        <li>[Point 2 with <strong>key terms</strong> highlighted]</li>
    </ul>
    
    <div class="key-highlight">
        <h3>Key Highlight:</h3>
        <blockquote>[Important quote or highlight related to the answer]</blockquote>
    </div>
</div>`;

    try {
        const response = await fetch(`${DeepSeek_BASE_URL}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: DeepSeek_MODEL,
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                max_tokens: 200,
                temperature: 0.7
            })
        });
        const data = await response.json();
        return data.choices[0].message.content;
    } catch (error) {
        throw new Error(`API request failed: ${error.message}`);
    }
}

// Helper function to handle fetch with retry for 429 errors
async function fetchWithRetry(url, options, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json();
                if (response.status === 429) {
                    console.warn(`Rate limit exceeded. Retrying in ${delay / 1000} seconds...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                    delay *= 2; // Exponential backoff
                    continue;
                } else {
                    throw new Error(`API request failed with status ${response.status}: ${errorData.error?.message || 'Unknown error'}`);
                }
            }
            return await response.json();
        } catch (error) {
            if (i === retries - 1) {
                throw error; // Rethrow the last error
            }
            console.error(`Fetch attempt ${i + 1} failed. Retrying...`);
        }
    }
}

// Function to get API key from storage
async function getApiKey() {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(['DeepSeek_API_KEY'], (result) => {
            if (result.DeepSeek_API_KEY) {
                resolve(result.DeepSeek_API_KEY);
            } else {
                reject(new Error('API key not found in storage'));
            }
        });
    });
}

// Function to set API key in storage
function setApiKey(apiKey) {
    chrome.storage.local.set({ 'DeepSeek_API_KEY': apiKey }, () => {
        console.log('API key stored successfully');
    });
}

// Example usage to set the API key (you can call this from a settings page or similar)
// setApiKey('sk-1577baabe3574262b21c2e2f249ac597');

// Configure marked options
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
});

// Function to safely render markdown
function renderMarkdown(content) {
    try {
        return marked.parse(content);
    } catch (error) {
        console.error('Error parsing markdown:', error);
        return content;
    }
}

// Function to clean model output
function cleanModelOutput(output) {
    // Remove ```html and ``` if present
    return output.replace(/^```html\n?/, '').replace(/```$/, '').trim();
}

// Update the display functions to use cleaned output
function displaySummary(summary) {
    const summaryElement = document.getElementById('summary');
    summaryElement.innerHTML = cleanModelOutput(summary);
    summaryElement.classList.remove('hidden');
}

function displayAnswer(answer) {
    const answerContainer = document.getElementById('answer-container');
    answerContainer.innerHTML = cleanModelOutput(answer);
}
