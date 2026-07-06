import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import useSpeechRecognition from "../hooks/useSpeechRecognition";
import "./Agent.css";

function Agent() {
  const [scenario, setScenario] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [result, setResult] = useState(null);
  const [user, setUser] = useState(null);
  const [language, setLanguage] = useState("en");
  const [voices, setVoices] = useState([]);
  const [speakingSection, setSpeakingSection] = useState(null);
  const navigate = useNavigate();
  
  const guidanceRef = useRef(null);
  const judgmentsRef = useRef(null);
  const complaintRef = useRef(null);

  const { isListening, startListening, stopListening } = useSpeechRecognition(language);

  const translations = {
    en: {
      title: "AI Legal Agent",
      subtitle: "Comprehensive Legal Analysis System",
      welcome: "Welcome",
      describe: "Describe Your Legal Scenario",
      placeholder: "Provide detailed information about your legal situation...",
      speak: "Speak",
      stop: "Stop",
      analyze: "Analyze Scenario",
      analyzing: "Analyzing Your Scenario",
      wait: "Please wait while we process your legal case...",
      guidance: "Legal Guidance & Analysis",
      cases: "Similar Legal Cases",
      complaint: "Generated Complaint Letter",
      next: "Next",
      viewCases: "View Similar Cases",
      generateLetter: "Generate Complaint Letter",
      viewDetails: "View Full Details",
      download: "Download PDF",
      newAnalysis: "New Analysis",
      match: "Match",
      pages: "pages"
    },
    ta: {
      title: "AI சட்ட முகவர்",
      subtitle: "விரிவான சட்ட பகுப்பாய்வு அமைப்பு",
      welcome: "வரவேற்கிறோம்",
      describe: "உங்கள் சட்ட சூழ்நிலையை விவரிக்கவும்",
      placeholder: "உங்கள் சட்ட நிலைமை பற்றிய விரிவான தகவலை வழங்கவும்...",
      speak: "பேசு",
      stop: "நிறுத்து",
      analyze: "பகுப்பாய்வு செய்",
      analyzing: "உங்கள் சூழ்நிலையை பகுப்பாய்வு செய்கிறது",
      wait: "உங்கள் சட்ட வழக்கை செயலாக்கும் வரை காத்திருக்கவும்...",
      guidance: "சட்ட வழிகாட்டுதல் & பகுப்பாய்வு",
      cases: "ஒத்த சட்ட வழக்குகள்",
      complaint: "உருவாக்கப்பட்ட புகார் கடிதம்",
      next: "அடுத்தது",
      viewCases: "ஒத்த வழக்குகளைப் பார்க்கவும்",
      generateLetter: "புகார் கடிதத்தை உருவாக்கவும்",
      viewDetails: "முழு விவரங்களைப் பார்க்கவும்",
      download: "PDF பதிவிறக்கம்",
      newAnalysis: "புதிய பகுப்பாய்வு",
      match: "பொருத்தம்",
      pages: "பக்கங்கள்"
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  useEffect(() => {
    window.speechSynthesis.cancel();
    setSpeakingSection(null);
  }, [language]);

  useEffect(() => {
    if (step === 1 && guidanceRef.current && result) {
      guidanceRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (step === 2 && judgmentsRef.current && result) {
      judgmentsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (step === 3 && complaintRef.current && result) {
      complaintRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [step, result]);

  const handleAnalyze = async () => {
    if (!scenario.trim() || !user) return;

    setLoading(true);
    setStep(1);
    setResult(null);
    
    try {
      const response = await API.post("/agent", {
        message: scenario,
        email: user.email,
        language: language
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("Error processing request");
      setStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((transcript) => {
        setScenario(transcript);
      });
    }
  };

  const speakText = (text, section) => {
    if (!window.speechSynthesis) {
      alert("Text-to-Speech not supported in this browser.");
      return;
    }

    if (speakingSection === section) {
      window.speechSynthesis.cancel();
      setSpeakingSection(null);
      return;
    }

    window.speechSynthesis.cancel();

    // Clean text: remove markdown symbols and HTML tags
    const cleanText = text
      .replace(/<[^>]*>/g, '')     // Remove HTML tags
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

    utterance.onstart = () => setSpeakingSection(section);
    utterance.onend = () => setSpeakingSection(null);

    window.speechSynthesis.speak(utterance);
  };

  const handleNext = () => {
    setStep(step + 1);
  };

  const handleDownloadPDF = async () => {
    if (!result?.complaint_letter) return;
    
    try {
      const response = await API.post("/generate_pdf", {
        text: result.complaint_letter,
        language: language
      }, {
        responseType: "blob"
      });
      
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "complaint_letter.pdf";
      a.click();
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleViewJudgment = (judgment) => {
    sessionStorage.setItem('agentState', JSON.stringify({
      scenario,
      step,
      result
    }));
    navigate("/judgment-detail", { state: { judgment } });
  };

  const handleReset = () => {
    setStep(0);
    setScenario("");
    setResult(null);
    sessionStorage.removeItem('agentState');
  };

  // Restore state on component mount
  useEffect(() => {
    const savedState = sessionStorage.getItem('agentState');
    if (savedState) {
      const { scenario: savedScenario, step: savedStep, result: savedResult } = JSON.parse(savedState);
      setScenario(savedScenario);
      setStep(savedStep);
      setResult(savedResult);
      sessionStorage.removeItem('agentState');
    }
  }, []);

  if (!user) return <div className="loading">Loading...</div>;

  return (
    <div className="agent-professional-container">
      <div className="agent-pro-header">
        <h1>⚖️ {translations[language].title}</h1>
        <p>{translations[language].subtitle}</p>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            onClick={() => setLanguage("en")}
            style={{ fontWeight: language === "en" ? "bold" : "normal", padding: "5px 10px" }}
          >
            English
          </button>
          <button
            onClick={() => setLanguage("ta")}
            style={{ fontWeight: language === "ta" ? "bold" : "normal", padding: "5px 10px" }}
          >
            தமிழ்
          </button>
          <span className="user-badge">{translations[language].welcome}, {user?.name}</span>
        </div>
      </div>

      {/* Step 0: Input */}
      {step === 0 && (
        <div className="step-container fade-in">
          <div className="input-card">
            <h2>📝 {translations[language].describe}</h2>
            <textarea
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              placeholder={translations[language].placeholder}
              rows="6"
            />
            <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
              <button
                className={`mic-button ${isListening ? "listening" : ""}`}
                onClick={handleMicClick}
                style={{ padding: "10px 20px" }}
              >
                {isListening ? `🎙️ ${translations[language].stop}` : `🎤 ${translations[language].speak}`}
              </button>
              <button onClick={handleAnalyze} disabled={!scenario.trim()} className="primary-btn">
                🔍 {translations[language].analyze}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-card">
            <div className="spinner"></div>
            <h2>🔍 {translations[language].analyzing}</h2>
            <p>{translations[language].wait}</p>
          </div>
        </div>
      )}

      {/* Step 1: Legal Guidance */}
      {step >= 1 && result && (
        <div className="step-container fade-in" ref={guidanceRef}>
          <div className="progress-bar">
            <div className={`progress-step ${step === 1 ? 'active' : ''}`} onClick={() => result && setStep(1)}>
              {translations[language].guidance}
            </div>
            <div className={`progress-step ${step === 2 ? 'active' : ''}`} onClick={() => result && setStep(2)}>
              {translations[language].cases}
            </div>
            <div className={`progress-step ${step === 3 ? 'active' : ''}`} onClick={() => result && setStep(3)}>
              {translations[language].complaint}
            </div>
            <div className={`progress-step ${step === 4 ? 'active' : ''}`} onClick={() => result && setStep(4)}>
              {language === 'en' ? 'Advocates' : 'வக்கீல்கள்'}
            </div>
          </div>
          
          {step === 1 && (
            <div className="content-card">
              <h2>📚 {translations[language].guidance}</h2>
              <div className="guidance-content" dangerouslySetInnerHTML={{ 
                __html: result?.guidance.replace(/\n/g, '<br/>').replace(/##/g, '<h3>').replace(/\*\*/g, '<strong>') 
              }} />
              <button
                className="speaker-button"
                onClick={() => speakText(result?.guidance, "guidance")}
                style={{ marginTop: "10px", marginRight: "10px" }}
              >
                {speakingSection === "guidance" ? `⏹ ${translations[language].stop}` : `🔊 ${translations[language].speak}`}
              </button>
              <button onClick={handleNext} className="primary-btn">{translations[language].next}: {translations[language].viewCases} →</button>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Judgments */}
      {step >= 2 && result && (
        <div className="step-container fade-in" ref={judgmentsRef}>
          {step === 2 && (
            <div className="content-card">
              <h2>⚖️ {translations[language].cases}</h2>
              <div className="judgments-grid">
                {result?.judgments.map((judgment, idx) => (
                  <div key={idx} className="judgment-card-pro">
                    <div className="judgment-header-pro">
                      <span className="rank-badge">#{judgment.rank}</span>
                      <span className="similarity-badge">{judgment.similarity}% {translations[language].match}</span>
                      <span className={`outcome-badge outcome-${judgment.outcome.toLowerCase()}`}>
                        {judgment.outcome}
                      </span>
                    </div>
                    <h3>{judgment.case_title}</h3>
                    <div className="judgment-meta">
                      <span>📅 {judgment.year}</span>
                      <span>📄 {judgment.page_count} {translations[language].pages}</span>
                    </div>
                    <p className="judgment-excerpt">{judgment.background.substring(0, 150)}...</p>
                    <button onClick={() => handleViewJudgment(judgment)} className="secondary-btn">
                      {translations[language].viewDetails} →
                    </button>
                  </div>
                ))}
              </div>
              <button onClick={handleNext} className="primary-btn">{translations[language].next}: {translations[language].generateLetter} →</button>
            </div>
          )}
        </div>
      )}

      {/* Step 3: Complaint Letter */}
      {step >= 3 && result && (
        <div className="step-container fade-in" ref={complaintRef}>
          {step === 3 && (
            <>
              <div className="content-card">
                <h2>📄 {translations[language].complaint}</h2>
                <div className="complaint-preview-pro">
                  <pre>{result?.complaint_letter}</pre>
                </div>
                <button
                  className="speaker-button"
                  onClick={() => speakText(result?.complaint_letter, "complaint")}
                  style={{ marginTop: "10px", marginBottom: "10px" }}
                >
                  {speakingSection === "complaint" ? `⏹ ${translations[language].stop}` : `🔊 ${translations[language].speak}`}
                </button>
                <div className="action-buttons">
                  <button onClick={handleDownloadPDF} className="primary-btn">
                    📥 {translations[language].download}
                  </button>
                  <button onClick={handleNext} className="primary-btn">
                    {translations[language].next}: {language === 'en' ? 'Find Advocates' : 'வக்கீல்களைக் கண்டறியவும்'} →
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Step 4: Advocates */}
      {step >= 4 && result && (
        <div className="step-container fade-in">
          {step === 4 && (
            <div className="content-card">
              <h2>👨⚖️ {language === 'en' ? 'Recommended Advocates' : 'பரிந்துரைக்கப்பட்ட வக்கீல்கள்'}</h2>
              {result?.advocates && result.advocates.length > 0 ? (
                <>
                  <p style={{ marginBottom: "20px", color: "#666" }}>
                    {language === 'en' 
                      ? 'Based on your district and case type:' 
                      : 'உங்கள் மாவட்டம் மற்றும் வழக்கு வகையை அடிப்படையாக:'}
                  </p>
                  <div className="advocates-list">
                    {result.advocates.map((advocate, idx) => (
                      <div key={idx} className="advocate-item">
                        <div className="advocate-info">
                          <h3>{advocate.name}</h3>
                          <span className="advocate-district">{advocate.city.toUpperCase()}</span>
                        </div>
                        <div className="advocate-practice">
                          {advocate.practice_areas.map((area, i) => (
                            <span key={i} className="practice-tag">{area}</span>
                          ))}
                        </div>
                        <a href={advocate.profile} target="_blank" rel="noopener noreferrer" className="advocate-link">
                          {language === 'en' ? 'View Profile' : 'சுயவிவரம் பார்க்க'} →
                        </a>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p style={{ textAlign: "center", color: "#666", padding: "2rem" }}>
                  {language === 'en' 
                    ? 'No advocates found for your district. Please update your profile with a valid district.' 
                    : 'உங்கள் மாவட்டத்திற்கு வக்கீல்கள் கிடைக்கவில்லை. சரியான மாவட்டத்துடன் உங்கள் சுயவிவரத்தைப் புதுப்பிக்கவும்.'}
                </p>
              )}
              <div className="action-buttons" style={{ marginTop: "2rem" }}>
                <button onClick={handleReset} className="secondary-btn">
                  🔄 {translations[language].newAnalysis}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Agent;
