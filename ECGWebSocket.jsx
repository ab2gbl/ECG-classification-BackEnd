import React, { useState, useEffect, useRef } from "react";
import ECGUploader from "./ECGUploader";

const ECGWebSocket = () => {
  const [signal, setSignal] = useState([]);
  const [chunkSize, setChunkSize] = useState(6);
  const [intervalData, setIntervalData] = useState(null);
  const [startChunk, setStartChunk] = useState(false);
  const [responses, setResponses] = useState([]);
  const [error, setError] = useState(null);
  const indexRef = useRef(0);
  const requestIdRef = useRef(0);
  const chunkCounterRef = useRef(0);
  const ws = useRef(null);

  const generateRequestId = () => {
    return `req_${Date.now()}_${requestIdRef.current++}`;
  };

  const generateChunkName = () => {
    return `chunk_${chunkCounterRef.current++}`;
  };

  const setupWebSocket = () => {
    if (ws.current) {
      ws.current.close();
    }

    ws.current = new WebSocket("ws://localhost:8000/ws/ecg/");

    ws.current.onopen = () => {
      console.log("WebSocket connected ✅");
      setError(null);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Received data from backend:", data);

      if (data.status === "error") {
        setError(data.message);
        if (data.message.includes("busy")) {
          // Stop streaming if system is busy
          setStartChunk(false);
        }
      } else if (data.status === "success") {
        setResponses((prev) => [...prev, data].slice(-10));
        setError(null);
      }
    };

    ws.current.onerror = (e) => {
      console.error("WebSocket error", e);
      setError("WebSocket connection error");
    };

    ws.current.onclose = () => {
      console.log("WebSocket closed ❌");
    };
  };

  useEffect(() => {
    setupWebSocket();
    return () => ws.current?.close();
  }, []);

  useEffect(() => {
    indexRef.current = 0;
    chunkCounterRef.current = 0;
  }, [signal]);

  const sendChunk = () => {
    const currentIndex = indexRef.current;
    const nextChunk = signal.slice(
      currentIndex,
      currentIndex + chunkSize * 250
    );

    if (nextChunk.length === 0) {
      setStartChunk(false);
      return;
    }

    setIntervalData({
      data: nextChunk,
      chunkName: generateChunkName(),
    });
    indexRef.current += nextChunk.length;
  };

  useEffect(() => {
    if (!startChunk || signal.length === 0) return;

    sendChunk(); // First chunk immediately

    const timer = setInterval(() => {
      sendChunk();
    }, chunkSize * 1000);

    return () => clearInterval(timer);
  }, [startChunk, signal, chunkSize]);

  useEffect(() => {
    if (
      ws.current &&
      ws.current.readyState === WebSocket.OPEN &&
      intervalData
    ) {
      const requestId = generateRequestId();
      console.log(`Sending chunk to backend (${requestId}):`, intervalData);
      ws.current.send(
        JSON.stringify({
          request_id: requestId,
          chunk_name: intervalData.chunkName,
          signal: intervalData.data,
        })
      );
    }
  }, [intervalData]);

  return (
    <div>
      <h1>ECG Signal Upload and Streaming</h1>

      <ECGUploader
        onSignalReceived={(sig) => {
          setSignal(sig);
          indexRef.current = 0;
          chunkCounterRef.current = 0;
        }}
      />

      <h2>Signal Length: {signal.length}</h2>

      <div>
        <label>Chunk Size (seconds): </label>
        <input
          type="number"
          value={chunkSize}
          onChange={(e) => setChunkSize(Number(e.target.value))}
          min="2"
          max="30"
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <button
          onClick={() => {
            setStartChunk(!startChunk);
            console.log("Streaming:", !startChunk);
            setupWebSocket();
          }}
        >
          {startChunk ? "Stop" : "Start"} Streaming
        </button>

        <button
          onClick={() => {
            indexRef.current = 0;
            chunkCounterRef.current = 0;
            setIntervalData(null);
            setStartChunk(false);
            setResponses([]);
            setError(null);
            console.log("Reset done");
          }}
        >
          Reset
        </button>

        <button onClick={setupWebSocket}>🔄 Reconnect WebSocket</button>
      </div>

      {error && (
        <div style={{ color: "red", marginTop: "10px" }}>Error: {error}</div>
      )}

      <div style={{ marginTop: "20px" }}>
        <h3>Current Status:</h3>
        <p>Streaming: {startChunk ? "✅ Active" : "⏸️ Paused"}</p>
        <p>
          {intervalData === null
            ? "No interval data available"
            : `Chunk ${intervalData.chunkName} (${indexRef.current / 250} - ${
                indexRef.current / 250 + chunkSize
              }s): ${intervalData.data.slice(0, 4).join(" ")} 
                \n ... \n 
              ${intervalData.data.slice(-4).join(" ")}`}
        </p>
      </div>

      <div>
        <h3>Backend Responses (Last 10):</h3>
        {responses.map((response, index) => (
          <div
            key={response.request_id}
            style={{
              marginBottom: "10px",
              padding: "10px",
              border: "1px solid #ccc",
            }}
          >
            <p>Response #{index + 1}</p>
            <p>Chunk Name: {response.chunk_name}</p>
            <p>Request ID: {response.request_id}</p>
            <pre>
              {response.result?.features
                ? JSON.stringify(response.result.features, null, 2)
                : "No features received."}
            </pre>
          </div>
        ))}
        {responses.length === 0 && <p>No responses received yet.</p>}
      </div>
    </div>
  );
};

export default ECGWebSocket;
