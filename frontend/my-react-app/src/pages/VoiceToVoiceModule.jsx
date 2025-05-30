import React, { useState, useRef } from 'react';
import { processVoiceToVoice } from '../api/api';
import './ModulePage.css'; // Common module CSS

function VoiceToVoiceModule() {
  const [audioFile, setAudioFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [outputVoiceBase64, setOutputVoiceBase64] = useState(''); // Base64 audio from backend
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const audioPlayerRef = useRef(null); // For the output audio

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      setAudioFile(file);
      setError(null);
    } else {
      setAudioFile(null);
      setError('Please upload a valid audio file.');
    }
  };

  const handleProcessVoice = async () => {
    setLoading(true);
    setError(null);
    setTranscription('');
    setOutputVoiceBase64('');

    if (!audioFile) {
      setError('Please select an audio file first.');
      setLoading(false);
      return;
    }

    try {
      // Assuming processVoiceToVoice handles sending FormData
      const response = await processVoiceToVoice(audioFile);
      setTranscription(response.data.transcription || 'No transcription.');
      setOutputVoiceBase64(response.data.audio_base64 || ''); // Assuming backend returns base64
    } catch (err) {
      console.error('Voice-to-voice processing failed:', err);
      setError(err.response?.data?.error || err.message || 'Failed to process voice.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="module-page voice-to-voice-module">
      <h2>Voice to Voice Module</h2>
      <p className="module-description">
        Upload an audio file to get a transcription and an AI-generated voice response.
      </p>
      <div className="input-area">
        <label htmlFor="audio-upload">Upload Audio File:</label>
        <input type="file" id="audio-upload" accept="audio/*" onChange={handleFileChange} />
        {audioFile && <p>Selected file: {audioFile.name}</p>}
      </div>
      <button onClick={handleProcessVoice} disabled={loading || !audioFile}>
        {loading ? 'Processing...' : 'Process Voice'}
      </button>
      {error && <p className="error-message">{error}</p>}

      {transcription && (
        <div className="output-area">
          <h3>Transcription:</h3>
          <p>{transcription}</p>
        </div>
      )}

      {outputVoiceBase64 && (
        <div className="output-area">
          <h3>AI Voice Response:</h3>
          <audio controls src={`data:audio/mp3;base64,${outputVoiceBase64}`} ref={audioPlayerRef}>
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
}

export default VoiceToVoiceModule;