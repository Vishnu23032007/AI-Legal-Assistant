import { useState, useRef } from "react";

const useSpeechRecognition = (language) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = (onResult) => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = language === "ta" ? "ta-IN" : "en-US";
    recognition.continuous = true;     // 🔥 Keep listening
    recognition.interimResults = true; // 🔥 Live typing

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let transcript = "";

      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }

      onResult(transcript);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();

    recognitionRef.current = recognition;

    // 🔥 Store globally so we can stop manually
    window.speechRecognitionInstance = recognition;
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  return { isListening, startListening, stopListening };
};

export default useSpeechRecognition;