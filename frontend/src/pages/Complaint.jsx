import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import API from "../services/api";
import useSpeechRecognition from "../hooks/useSpeechRecognition";
import "./complaint.css";

function Complaint() {

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const [voices, setVoices] = useState([]);
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const [user, setUser] = useState(null);

  const chatEndRef = useRef(null);
  const navigate = useNavigate();

  const { isListening, startListening, stopListening } =
    useSpeechRecognition(language);

  // Check if user is logged in
  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  // Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load voices
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  // UI translations
  const translations = {
    en: {
      title: "Complaint AI Assistant",
      placeholder: "Describe your issue...",
      send: "Send",
      typing: "AI is typing...",
      error: "Error connecting to server.",
      success: "✅ Your complaint letter has been generated and downloaded successfully."
    },
    ta: {
      title: "புகார் AI உதவியாளர்",
      placeholder: "உங்கள் பிரச்சினையை விவரிக்கவும்...",
      send: "அனுப்பு",
      typing: "AI எழுதுகிறது...",
      error: "சர்வருடன் இணைப்பு பிழை.",
      success: "✅ உங்கள் புகார் கடிதம் வெற்றிகரமாக உருவாக்கப்பட்டு பதிவிறக்கம் செய்யப்பட்டது."
    }
  };

  // Send Message
  const sendMessage = async () => {

    if (!message.trim() || !user) return;

    const userMessage = { sender: "user", text: message };

    setMessages((prev) => [...prev, userMessage]);
    setMessage("");

    try {

      setLoading(true);

      const response = await API.post(
        "/complaint",
        {
          message: userMessage.text,
          language: language,
          email: user.email
        },
        {
          responseType: "blob"
        }
      );

      const contentType = response.headers["content-type"];

      // CASE 1: PDF returned
      if (contentType === "application/pdf") {

        const blob = new Blob([response.data], { type: "application/pdf" });

        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "complaint.pdf";

        document.body.appendChild(a);
        a.click();
        a.remove();

        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: translations[language].success }
        ]);

      }

      // CASE 2: JSON returned (continue conversation)
      else {

        const text = await response.data.text();
        const data = JSON.parse(text);

        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text: data.message || "Please provide more details."
          }
        ]);
      }

    } catch (error) {

      console.error(error);

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: translations[language].error }
      ]);

    } finally {

      setLoading(false);

    }

  };

  // Mic Toggle
  const handleMicClick = () => {

    if (isListening) {

      stopListening();

    } else {

      startListening((transcript) => {
        setMessage(transcript);
      });

    }

  };

  // Text To Speech
  const speakText = (text, index) => {

    if (!window.speechSynthesis) return;

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

    if (selectedVoice) utterance.voice = selectedVoice;

    utterance.onstart = () => setSpeakingIndex(index);
    utterance.onend = () => setSpeakingIndex(null);

    window.speechSynthesis.speak(utterance);

  };

  // Stop speech on language change
  useEffect(() => {
    window.speechSynthesis.cancel();
    setSpeakingIndex(null);
  }, [language]);

  if (!user) return <div>Loading...</div>;

  return (
    

      <div className="complaint-container">

        {/* Header */}
        <div className="complaint-header">

          <span>{translations[language].title}</span>

          <div className="lang-buttons">

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

          </div>

        </div>

        {/* Chat Window */}
        <div className="chat-window">

          {messages.map((msg, index) => (

            <div key={index} className={`message-row ${msg.sender}`}>

              <div className={`message-bubble ${msg.sender}`}>

                {msg.text}

                {msg.sender === "bot" && (

                  <button
                    className="speaker-button"
                    onClick={() => speakText(msg.text, index)}
                  >
                    {speakingIndex === index ? "⏹ Stop" : "🔊 Speak"}
                  </button>

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

        {/* Input */}
        <div className="chat-input-row">

          <input
            className="chat-input"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={translations[language].placeholder}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
          />

          <button
            className={`mic-button ${isListening ? "listening" : ""}`}
            onClick={handleMicClick}
          >
            {isListening ? "🎙 Stop" : "🎤 Speak"}
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

    
  );
}

export default Complaint;