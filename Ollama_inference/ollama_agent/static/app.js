class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            input: '',
            models: [],
            selectedModel: 'deepseek-r1:32b',
            isLoading: false
        };
        this.messagesEnd = React.createRef();
    }

    componentDidMount() {
        this.fetchModels();
    }

    componentDidUpdate() {
        this.scrollToBottom();
    }

    scrollToBottom() {
        if (this.messagesEnd.current) {
            this.messagesEnd.current.scrollIntoView({ behavior: "smooth" });
        }
    }

    fetchModels = async () => {
        try {
            const response = await fetch('http://localhost:8000/models');
            const data = await response.json();
            this.setState({ models: data.models });
        } catch (error) {
            console.error('Error fetching models:', error);
        }
    }

    handleSubmit = async (e) => {
        e.preventDefault();
        if (!this.state.input.trim() || this.state.isLoading) return;

        const userMessage = this.state.input;
        this.setState(state => ({
            messages: [...state.messages, { text: userMessage, sender: 'user' }],
            input: '',
            isLoading: true
        }));

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    model: this.state.selectedModel
                }),
            });

            const data = await response.json();
            this.setState(state => ({
                messages: [...state.messages, { text: data.response, sender: 'bot' }],
                isLoading: false
            }));
        } catch (error) {
            console.error('Error:', error);
            this.setState(state => ({
                messages: [...state.messages, { text: 'Error: Could not get response from the server.', sender: 'bot' }],
                isLoading: false
            }));
        }
    }

    render() {
        return (
            <div className="container">
                <div className="localhost-indicator">
                    <i className="material-icons">wifi</i>
                    Running on localhost
                </div>
                
                <div className="header">
                    <h1>
                        <i className="material-icons" style={{ verticalAlign: 'middle', marginRight: '8px' }}>chat</i>
                        Local Chatbot
                    </h1>
                    <div className="model-selector">
                        <select 
                            value={this.state.selectedModel}
                            onChange={(e) => this.setState({ selectedModel: e.target.value })}
                        >
                            {this.state.models.map(model => (
                                <option key={model.name} value={model.name}>
                                    {model.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="chat-container">
                    <div className="messages">
                        {this.state.messages.map((message, index) => (
                            <div 
                                key={index} 
                                className={`message ${message.sender}-message`}
                            >
                                {message.text}
                            </div>
                        ))}
                        {this.state.isLoading && (
                            <div className="message bot-message">
                                <i className="material-icons" style={{ animation: 'spin 1s linear infinite' }}>sync</i>
                                Thinking...
                            </div>
                        )}
                        <div ref={this.messagesEnd} />
                    </div>

                    <form onSubmit={this.handleSubmit} className="input-container">
                        <input
                            type="text"
                            value={this.state.input}
                            onChange={(e) => this.setState({ input: e.target.value })}
                            placeholder="Type your message..."
                            disabled={this.state.isLoading}
                        />
                        <button type="submit" disabled={this.state.isLoading}>
                            <i className="material-icons">send</i>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('root'));
