document.addEventListener('DOMContentLoaded', () => {
    const API_KEY = "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";
    
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

    async function generateSuggestedQuestions(summary) {
        const prompt = `基于这段总结，生成3个最重要的后续问题。请用中文回答，以JSON数组格式返回。示例：["问题1？", "问题2？", "问题3？"]。问题应该简洁且有针对性：\n\n${summary}`;

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
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

// Function to generate summary using ChatGPT
async function generateSummary(content, length, apiKey) {
    const maxLength = {
        short: 100,
        medium: 200,
        long: 400
    }[length] || 200;

    const prompt = `请用中文总结以下内容，重点突出主要信息。总结长度限制在${maxLength}字以内。请以HTML格式返回，使用<h2>标题</h2>和<ul><li>要点</li></ul>的形式组织内容：\n\n${content}`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [
                {
                    role: 'user',
                    content: prompt
                }
            ],
            max_tokens: maxLength * 2,
            temperature: 0.7
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Failed to generate summary');
    }

    const data = await response.json();
    return data.choices[0].message.content.trim();
}

// Function to generate answer using ChatGPT
async function generateAnswer(question, summary, apiKey) {
    const prompt = `基于这段总结:\n${summary}\n\n请回答这个问题:\n${question}`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: 'gpt-3.5-turbo',
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
        const error = await response.json();
        throw new Error(error.error?.message || 'Failed to generate answer');
    }

    const data = await response.json();
    return data.choices[0].message.content.trim();
}

// Function to show notification
function showNotification(message, isError = false) {
    const notification = document.createElement('div');
    notification.className = `notification ${isError ? 'error' : 'success'}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
