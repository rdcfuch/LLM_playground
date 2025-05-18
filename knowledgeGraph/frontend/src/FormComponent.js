import React, { useState } from 'react';
import axios from 'axios';

const FormComponent = () => {
  const [inputText, setInputText] = useState('');
  const [graphHtml, setGraphHtml] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [serverResponse, setServerResponse] = useState('');
  const [isSuccessful, setIsSuccessful] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    
    setLoading(true);
    setError('');
    setIsSuccessful(false);
    
    try {
      const response = await axios.post('http://localhost:8000/generate-graph/', {
        text: inputText
      });
      
      setGraphHtml(response.data.html_source);
      // Display full server response
      setServerResponse(JSON.stringify(response.data, null, 2));
      setInputText('');
      setIsSuccessful(true);
    } catch (err) {
      setError('Failed to generate graph. Please try again.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter your text paragraph here..."
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={loading}
            className={loading ? 'loading' : ''}
          >
            {loading ? 'Generating...' : 'Generate Graph'}
          </button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </form>
      
      {graphHtml && (
        <div className="graph-container">
          {isSuccessful && (
            <a href="http://localhost:3000/graph_from_api.html" 
               target="_blank" 
               rel="noopener noreferrer"
               className="graph-link">
              Open Full Screen Visualization
            </a>
          )}
          <div dangerouslySetInnerHTML={{ __html: graphHtml }} />
        </div>
      )}
      
      {serverResponse && (
        <div className="server-response">
          <h3>Server Response:</h3>
          <pre>{serverResponse}</pre>
        </div>
      )}
    </div>
  );
};

export default FormComponent;