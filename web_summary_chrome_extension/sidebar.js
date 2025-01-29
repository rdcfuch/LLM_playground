// DeepSeek API Configuration
const DeepSeek_MODEL = "deepseek-chat";
const DeepSeek_BASE_URL = "https://api.deepseek.com";
const API_KEY = "sk-1577baabe3574262b21c2e2f249ac597";

document.addEventListener('DOMContentLoaded', async () => {
    const summarizeButton = document.getElementById('summarize');
    const askQuestionButton = document.getElementById('ask-question');
    const lengthSelect = document.getElementById('length');
    const languageSelect = document.getElementById('language');
    const summaryElement = document.getElementById('summary');
    const loadingElement = document.getElementById('loading');
    const questionsSection = document.getElementById('questions-section');
    const questionInput = document.getElementById('question-input');
    const answerContainer = document.getElementById('answer-container');
    const suggestedQuestionsContainer = document.querySelector('.suggested-questions');

    // Check if there's a pending summarization request
    const result = await chrome.storage.local.get(['pendingSummarizeTabId', 'summaryLanguage']);
    if (result.pendingSummarizeTabId) {
        // Clear the pending flag
        chrome.storage.local.remove('pendingSummarizeTabId');
        // Start summarizing immediately
        summarizeCurrentPage();
    }

    // Set default language to Chinese if not set
    chrome.storage.local.get(['summaryLanguage'], (result) => {
        if (!result.summaryLanguage) {
            chrome.storage.local.set({ 'summaryLanguage': 'chinese' });
        }
        // Update the language selector to match storage
        languageSelect.value = result.summaryLanguage || 'chinese';
    });

    // Set default length to medium and store preference
    chrome.storage.local.get(['summaryLength'], (result) => {
        if (!result.summaryLength) {
            chrome.storage.local.set({ 'summaryLength': 'medium' });
        }
        // Update the length selector to match storage
        lengthSelect.value = result.summaryLength || 'medium';
    });

    // Save preferences when changed
    lengthSelect.addEventListener('change', () => {
        chrome.storage.local.set({
            summaryLength: lengthSelect.value
        });
    });

    languageSelect.addEventListener('change', () => {
        chrome.storage.local.set({
            summaryLanguage: languageSelect.value
        });
    });

    async function generateSuggestedQuestions(summary) {
        const prompt = `Based on this summary, generate 3 follow-up questions that would be interesting to ask. Return them in a JSON array format. Example: ["Question 1?", "Question 2?", "Question 3?"]. Questions should be concise and focused:\n\n${summary}`;

        const response = await fetch(`${DeepSeek_BASE_URL}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
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

        if (!response.ok) {
            throw new Error('Failed to generate questions');
        }

        const data = await response.json();
        try {
            return JSON.parse(data.choices[0].message.content);
        } catch (e) {
            return [];
        }
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

            const answer = await generateAnswer(question, result.currentSummary, API_KEY);
            
            displayAnswer(answer);
        } catch (error) {
            answerContainer.textContent = 'Error: ' + error.message;
        }
    }

    async function summarizeCurrentPage() {
        loadingElement.classList.remove('hidden');
        summaryElement.classList.add('hidden');
        suggestedQuestionsContainer.classList.add('hidden');
        questionsSection.classList.add('hidden');

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (!tab) {
                throw new Error('No active tab found');
            }

            // Check if we have permission to access the tab
            try {
                const result = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    function: getPageContent
                });

                if (!result || !result[0] || !result[0].result) {
                    throw new Error('Could not extract content from the page');
                }

                const pageContent = result[0].result;
                if (!pageContent.trim()) {
                    throw new Error('No readable content found on the page');
                }

                const summary = await generateSummary(pageContent, lengthSelect.value, API_KEY);
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
                if (error.message.includes('Cannot access contents of')) {
                    throw new Error('Cannot access this page. The extension needs permission to read the page content.');
                } else {
                    throw error;
                }
            }
        } catch (error) {
            summaryElement.textContent = 'Error: ' + error.message;
            summaryElement.classList.remove('hidden');
        } finally {
            loadingElement.classList.add('hidden');
        }
    }

    // Listen for summarize button click
    summarizeButton.addEventListener('click', summarizeCurrentPage);

    // Listen for ask question button click
    askQuestionButton.addEventListener('click', () => {
        const question = questionInput.value.trim();
        if (!question) return;
        askQuestion(question);
    });

    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'triggerSummary') {
            summarizeCurrentPage();
        }
        return true;
    });

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

    async function generateSummary(content, length, apiKey) {
        const language = await chrome.storage.local.get(['summaryLanguage']).then(result => result.summaryLanguage || 'english');
        const languagePrompt = language === 'chinese' ? '请用中文（简体）总结。' : 'Please summarize in English.';
        
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

        const prompt = `${languagePrompt} Please provide a ${lengthPrompt} summary of the following webpage content. Return the response in HTML format with the following structure:

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

        if (!response.ok) {
            throw new Error('Failed to generate summary');
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }

    // Function to generate answer using DeepSeek API
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

        if (!response.ok) {
            throw new Error('Failed to generate answer');
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }

    // Function to clean model output
    function cleanModelOutput(output) {
        // Remove ```html and ``` if present
        return output.replace(/^```html\n?/, '').replace(/```$/, '').trim();
    }

    // Function to display summary
    function displaySummary(summary) {
        const summaryElement = document.getElementById('summary');
        summaryElement.innerHTML = cleanModelOutput(summary);
        summaryElement.classList.remove('hidden');
    }

    // Function to display answer
    function displayAnswer(answer) {
        const answerContainer = document.getElementById('answer-container');
        answerContainer.innerHTML = cleanModelOutput(answer);
    }
});

// Function to get page content
async function getPageContent() {
    // Get article content if available
    const article = document.querySelector('article');
    if (article) {
        return article.innerText;
    }

    // Get the main content if available
    const main = document.querySelector('main');
    if (main) {
        return main.innerText;
    }

    // If no specific content container is found, get all visible text
    const body = document.body;
    const walker = document.createTreeWalker(
        body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                const style = window.getComputedStyle(node.parentElement);
                return (style.display !== 'none' && style.visibility !== 'hidden')
                    ? NodeFilter.FILTER_ACCEPT
                    : NodeFilter.FILTER_REJECT;
            }
        }
    );

    let content = '';
    let node;
    while (node = walker.nextNode()) {
        content += node.textContent.trim() + '\n';
    }
    
    return content.trim();
}
