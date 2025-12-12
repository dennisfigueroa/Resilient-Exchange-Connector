import React, { useEffect, useState } from "react";

export default function App() {
  const [latestTrade, setLatestTrade] = useState(null);
  const [status, setStatus] = useState("connecting...");

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8001/ws/trades");

    socket.onopen = () => setStatus("connected ✅");

    socket.onmessage = (event) => {
      const trade = JSON.parse(event.data);
      setLatestTrade(trade);
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      setStatus("error ❌");
    };

    socket.onclose = () => setStatus("disconnected ⚠️");

    return () => socket.close();
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: 20 }}>
      <h1>Resilient Exchange Dashboard</h1>
      <p>Status: {status}</p>
      {latestTrade ? (
        <div>
          <h2>{latestTrade.symbol}</h2>
          <p>Price: {latestTrade.price}</p>
          <p>Quantity: {latestTrade.qty}</p>
          <p>Timestamp: {new Date(latestTrade.ts).toLocaleTimeString()}</p>
        </div>
      ) : (
        <p>Waiting for trades...</p>
      )}
    </div>
  );
}
