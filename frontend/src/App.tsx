import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState<string>("Loading...");

  useEffect(() => {
    const apiUrl = "http://localhost:8000/";
    fetch(apiUrl)
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message || "Connected to backend");
      })
      .catch((err) => {
        console.error(err);
        setMessage("Error connecting to backend");
      });
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Git Analytics</h1>
      <p><strong>Backend status:</strong> {message}</p>
    </div>
  );
}

export default App;
