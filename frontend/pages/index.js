import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const detectAI = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.post(`${backendUrl}/detect`, { text });
      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert('Error detecting AI score');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>AI Text Humanizer</h1>
      <textarea
        rows="6"
        cols="50"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste your text here..."
        style={{ width: '100%', marginBottom: '1rem' }}
      />
      <button onClick={detectAI} disabled={loading}>
        {loading ? 'Detecting...' : 'Detect AI Score'}
      </button>
      {result && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Result</h2>
          <p>AI Score: {result.ai_score}%</p>
          <p>Confidence: {result.confidence}</p>
        </div>
      )}
    </div>
  );
}