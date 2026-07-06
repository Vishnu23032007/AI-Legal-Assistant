import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

import API from "../services/api";
import useSpeechRecognition from "../hooks/useSpeechRecognition";
import "./chatbot.css";

function ChatBot() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const [voices, setVoices] = useState([]);

  const chatEndRef = useRef(null);

  const { isListening, startListening, stopListening } =
    useSpeechRecognition(language);

  // ✅ Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ Load voices properly (IMPORTANT FIX)
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  // 🌍 UI TEXT
  const translations = {
    en: {
      title: "Legal AI Assistant",
      clear: "Clear Chat",
      placeholder: "Type your legal question...",
      send: "Send",
      typing: "AI is typing...",
      error: "Error connecting to server."
    },
    ta: {
      title: "சட்ட AI உதவியாளர்",
      clear: "அரட்டை அழி",
      placeholder: "உங்கள் சட்ட கேள்வியை எழுதுங்கள்...",
      send: "அனுப்பு",
      typing: "AI எழுதுகிறது...",
      error: "சர்வருடன் இணைப்பு பிழை."
    }
  };

  // ✅ Send Message
  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = { sender: "user", text: message };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await API.post("/chatbot", {
        message: message,
        language: language
      });

      const aiReply =
        res.data?.stage3?.response ||
        res.data?.response ||
        res.data?.reply ||
        "No response received.";

      setMessages((prev) => [...prev, { sender: "bot", text: aiReply }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: translations[language].error }
      ]);
    } finally {
      setLoading(false);
      setMessage("");
    }
  };

  // 🎤 Mic Toggle
  const handleMicClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((transcript) => {
        setMessage(transcript);
      });
    }
  };

  // 🔊 Text To Speech (FULL FIXED VERSION)
  const speakText = (text, index) => {
    if (!window.speechSynthesis) {
      alert("Text-to-Speech not supported in this browser.");
      return;
    }

    // Stop if clicking same message again
    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }

    window.speechSynthesis.cancel();

    // Clean text: remove markdown symbols
    const cleanText = text
      .replace(/#{1,6}\s?/g, '')  // Remove ## headings
      .replace(/\*\*/g, '')        // Remove bold **
      .replace(/\*/g, '')          // Remove italic *
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // Remove links [text](url)
      .replace(/`{1,3}[^`]*`{1,3}/g, '')  // Remove code blocks
      .replace(/[-_]{3,}/g, '')    // Remove horizontal rules
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);

    // 🔥 Find correct voice
    let selectedVoice = null;

    if (language === "ta") {
      selectedVoice = voices.find(
        (voice) =>
          voice.lang.toLowerCase().includes("ta") ||
          voice.name.toLowerCase().includes("tamil")
      );
    } else {
      selectedVoice = voices.find((voice) =>
        voice.lang.toLowerCase().includes("en")
      );
    }

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    } else {
      console.warn("No Tamil voice found. Using default voice.");
    }

    utterance.rate = 1;
    utterance.pitch = 1;

    utterance.onstart = () => setSpeakingIndex(index);
    utterance.onend = () => setSpeakingIndex(null);

    window.speechSynthesis.speak(utterance);
  };

  // ✅ Stop speaking when language changes
  useEffect(() => {
    window.speechSynthesis.cancel();
    setSpeakingIndex(null);
  }, [language]);

  const clearChat = async () => {
    const confirmClear = window.confirm(
      language === "en"
        ? "Are you sure you want to clear this conversation?"
        : "இந்த உரையாடலை அழிக்க விரும்புகிறீர்களா?"
    );

    if (!confirmClear) return;

    try {
      await API.post("/new_conversation");
      setMessages([]);
    } catch (error) {
      console.error("Error resetting conversation");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    
      <div className="chatbot-wrapper">

        {/* Header */}
        <div className="chatbot-header">
          <span>{translations[language].title}</span>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => setLanguage("en")}
              style={{ fontWeight: language === "en" ? "bold" : "normal" }}
            >
              English
            </button>

            <button
              onClick={() => setLanguage("ta")}
              style={{ fontWeight: language === "ta" ? "bold" : "normal" }}
            >
              தமிழ்
            </button>

            <button className="clear-btn" onClick={clearChat}>
              {translations[language].clear}
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="chatbot-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.sender}`}>
              <div className={`message-bubble ${msg.sender}`}>

                {msg.sender === "bot" ? (
                  <>
                    <ReactMarkdown>{msg.text}</ReactMarkdown>

                    <button
                      className="speaker-button"
                      onClick={() => speakText(msg.text, index)}
                    >
                      {speakingIndex === index ? "⏹ Stop" : "🔊 Speak"}
                    </button>
                  </>
                ) : (
                  msg.text
                )}

              </div>
            </div>
          ))}

          {loading && (
            <p className="typing-indicator">
              {translations[language].typing}
            </p>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="chatbot-input-area">
          <input
            className="chatbot-input"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={translations[language].placeholder}
          />

          <button
            className={`mic-button ${isListening ? "listening" : ""}`}
            onClick={handleMicClick}
          >
            {isListening ? "🎙️ Stop" : "🎤 Speak"}
          </button>

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={loading}
          >
            {translations[language].send}
          </button>
        </div>

      </div>
    /* </MainLayout> */
  );
}

export default ChatBot;