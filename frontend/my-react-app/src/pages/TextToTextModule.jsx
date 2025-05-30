import React, { useState } from 'react';
import { processTextToText } from '../api/api';
import './ModulePage.css'; // Common module CSS

function TextToTextModule() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleProcessText = async () => {
    setLoading(true);
    setError(null);
    setOutputText(''); // Clear previous output
    try {
      const response = await processTextToText(inputText);
      setOutputText(response.data.result || 'No result returned.'); // Adjust based on your API response structure
    } catch (err) {
      console.error('Text-to-text processing failed:', err);
      setError(err.response?.data?.error || err.message || 'Failed to process text.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="module-page text-to-text-module">
      <h2>Text to Text Module</h2>
      <p className="module-description">
        Input your text, and our AI will process it to provide insights, summaries,
        or transformations based on the backend logic.
      </p>
      <div className="input-area">
        <label htmlFor="input-text">Input Text:</label>
        <textarea
          id="input-text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter text here..."
          rows="8"
        />
      </div>
      <button onClick={handleProcessText} disabled={loading || !inputText.trim()}>
        {loading ? 'Processing...' : 'Process Text'}
      </button>
      {error && <p className="error-message">{error}</p>}
      {outputText && (
        <div className="output-area">
          <h3>Output:</h3>
          <p>{outputText}</p>
        </div>
      )}
    </div>
  );
}

export default TextToTextModule;