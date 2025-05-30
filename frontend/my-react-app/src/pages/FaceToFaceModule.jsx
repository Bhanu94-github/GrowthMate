import React, { useState, useRef } from 'react';
import { processFaceToFace } from '../api/api'; // API call

function FaceToFaceModule() {
  const [videoFile, setVideoFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setVideoFile(file);
  };

  const handleProcessFace = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await processFaceToFace(videoFile);
      setAnalysisResult(response.data.analysis); // Adjust
    } catch (err) {
      console.error('Face-to-face processing failed:', err);
      setError(err.message || 'Failed to process video.');
    } finally {
      setLoading(false);
    }
  };

  const playVideo = () => {
    if (videoRef.current) {
      videoRef.current.play();
    }
  };

  return (
    <div className="module-page face-to-face-module">
      <h2>Face to Face Module (Coming Soon)</h2>
      <div className="input-area">
        <label htmlFor="video-upload">Upload Video File:</label>
        <input type="file" id="video-upload" accept="video/*" onChange={handleFileChange} />
      </div>
      <button onClick={handleProcessFace} disabled={loading || !videoFile}>
        {loading ? 'Processing...' : 'Process Video'}
      </button>
      {error && <p className="error-message">{error}</p>}
      {analysisResult && (
        <div className="output-area">
          <h3>Analysis Result:</h3>
          <p>{analysisResult}</p>
        </div>
      )}
      {videoFile && (
        <div className="output-area">
          <h3>Uploaded Video:</h3>
          <video src={URL.createObjectURL(videoFile)} ref={videoRef} controls />
          <button onClick={playVideo}>Play</button>
        </div>
      )}
    </div>
  );
}

export default FaceToFaceModule;