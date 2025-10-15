import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { FaArrowUp } from "react-icons/fa";

const API_BASE = "http://localhost:8000/api/v1";

export default function App() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages]);

  const newSession = async () => {
    const res = await axios.post(`${API_BASE}/sessions`);
    setSessionId(res.data.session_id);
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;
    const newMsg = { role: "user", content: input, time: new Date().toLocaleTimeString() };
    setMessages((prev) => [...prev, newMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/sessions/${sessionId}/message`, {
        text: newMsg.content,
      });
      const reply = {
        role: "assistant",
        content: res.data.text,
        suggested_action: res.data.suggested_action,
        time: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, reply]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "⚠️ Could not reach backend.",
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const escalate = async () => {
    if (!sessionId) return;
    await axios.post(`${API_BASE}/sessions/${sessionId}/escalate`);
    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        content: "🔔 Escalation sent to human support.",
        time: new Date().toLocaleTimeString(),
      },
    ]);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-white p-6">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="backdrop-blur-xl bg-white/10 shadow-2xl rounded-3xl w-full max-w-2xl flex flex-col overflow-hidden border border-white/20"
      >
        {/* Header */}
        <header className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white p-4 flex justify-between items-center">
          <h1 className="text-lg font-semibold">AI Customer Support Bot</h1>
          <button
            onClick={newSession}
            className="bg-white text-indigo-700 font-semibold px-3 py-1 rounded-md hover:bg-indigo-100 transition"
          >
            New Chat
          </button>
        </header>

        {/* Chat Body */}
        <div ref={chatRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-white/10 backdrop-blur-sm">
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role !== "user" && (
                <img
                  src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
                  alt="bot"
                  className="w-8 h-8 rounded-full mr-2 shadow-md"
                />
              )}
              <div
                className={`p-3 rounded-2xl max-w-xs ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-none"
                    : msg.role === "assistant"
                    ? "bg-white text-gray-900 rounded-bl-none shadow"
                    : "bg-yellow-100 text-yellow-900 text-sm"
                }`}
              >
                {msg.content}
                {msg.suggested_action && (
                  <div className="text-xs mt-1 text-indigo-700">
                    Suggested: {msg.suggested_action.type}
                  </div>
                )}
                <div className="text-[10px] text-gray-400 mt-1 text-right">{msg.time}</div>
              </div>
              {msg.role === "user" && (
                <img
                  src="https://cdn-icons-png.flaticon.com/512/2202/2202112.png"
                  alt="user"
                  className="w-8 h-8 rounded-full ml-2 shadow-md"
                />
              )}
            </motion.div>
          ))}

          {loading && (
            <div className="text-gray-300 italic text-sm">HelpBot is typing...</div>
          )}
        </div>

        {/* Footer */}
        <footer className="p-4 bg-white/10 backdrop-blur-md flex space-x-2 border-t border-white/20">
          <input
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none text-gray-800"
            placeholder={sessionId ? "Type your message..." : "Click 'New Chat' to start"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button
            onClick={sendMessage}
            className="bg-indigo-600 text-white p-3 rounded-full hover:bg-indigo-700 transition"
          >
            <FaArrowUp />
          </button>
          <button
            onClick={escalate}
            className="bg-red-500 text-white px-4 rounded-full hover:bg-red-600 transition"
          >
            Escalate
          </button>
        </footer>
      </motion.div>
    </div>
  );
}
