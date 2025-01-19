document.addEventListener('DOMContentLoaded', async () => {
    const API_KEY = "sk-e2elzR10u4Tv2UXxx9kYC6Te0OrzM87qlpgHJsWVjzHd6Ouw";
    
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

    // Set default language to English if not already set
    if (!result.summaryLanguage) {
        chrome.storage.local.set({ summaryLanguage: 'english' });
    }
    languageSelect.value = result.summaryLanguage || 'english';

    // Always set to short and clear any existing preference
    lengthSelect.value = 'short';
    chrome.storage.local.set({ summaryLength: 'short' });

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

        const response = await fetch('https://api.moonshot.cn/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: 'moonshot-v1-8k',
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
            
            const answerElement = document.createElement('div');
            answerElement.textContent = answer;
            answerContainer.innerHTML = '';
            answerContainer.appendChild(answerElement);
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
                summaryElement.innerHTML = summary;
                summaryElement.classList.remove('hidden');
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

// Function to generate summary using Kimi API
async function generateSummary(content, length, apiKey) {
    const language = await chrome.storage.local.get(['summaryLanguage']).then(result => result.summaryLanguage || 'english');
    const languagePrompt = language === 'chinese' ? 'Please summarize in Chinese (简体中文).' : 'Please summarize in English.';
    
    const lengthPrompts = {
        short: "Provide a very concise summary in 2-3 sentences.",
        medium: "Provide a balanced summary in about 5-6 sentences.",
        long: "Provide a detailed summary in about 8-10 sentences."
    };

    const prompt = `${languagePrompt} Please provide a ${length} summary of the following webpage content:\n\n${content}`;

    const response = await fetch('https://api.moonshot.cn/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: 'moonshot-v1-8k',
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

// Function to generate answer using Kimi API
async function generateAnswer(question, summary, apiKey) {
    const prompt = `Based on this summary:\n${summary}\n\nPlease answer this question:\n${question}`;

    const response = await fetch('https://api.moonshot.cn/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: 'moonshot-v1-8k',
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
