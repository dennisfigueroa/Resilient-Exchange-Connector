import React, { useEffect, useState } from "react";

export default function App() {
  // We initialize state as null
  const [spreadData, setSpreadData] = useState(null);
  const [status, setStatus] = useState("connecting...");

  useEffect(() => {
    // 1. FIXED PORT (8000) and FIXED URL (singular /ws/spread)
    const socket = new WebSocket("ws://localhost:8000/ws/spread");

    socket.onopen = () => setStatus("connected ✅");

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received spread:", data);
        setSpreadData(data);
      } catch (e) {
        console.error("Error parsing JSON:", e);
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      setStatus("error ❌");
    };

    socket.onclose = () => setStatus("disconnected ⚠️");

    // Cleanup: Close the connection when the component unmounts
    return () => socket.close();
  }, []);

  return (
    <div style={{ fontFamily: "monospace", padding: 50, textAlign: "center", background: "#222", color: "white", minHeight: "100vh" }}>
      <h1>Crypto Spread Dashboard</h1>
      <p style={{ color: "#888" }}>Status: {status}</p>

      {spreadData ? (
        <div style={{ marginTop: 50 }}>
          {/* Display the Symbol */}
          <h2 style={{ fontSize: "2rem", color: "#4CAF50" }}>
            {spreadData.symbol}
          </h2>

          {/* Display the Spread Value */}
          <div style={{ 
            fontSize: "4rem", 
            fontWeight: "bold",
            color: spreadData.spread >= 0 ? "#00ff00" : "#ff4444" 
          }}>
            {spreadData.spread?.toFixed(4)}
          </div>

          <p style={{ marginTop: 20, color: "#aaa" }}>
            Exchanges: {spreadData.exchanges ? spreadData.exchanges.join(" vs ") : "Unknown"}
          </p>
        </div>
      ) : (
        <p style={{ marginTop: 50 }}>Waiting for live data...</p>
      )}
    </div>
  );
}