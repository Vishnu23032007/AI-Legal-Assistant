import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    }
    sessionStorage.removeItem('agentState');
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    
      <div className="dashboard-container">

        {/* Badge */}
        <span className="dashboard-badge">⚖️ Legal AI Platform</span>

        {/* Title */}
        <h1 className="dashboard-title">
          LAW <span className="highlight">SAKTHI</span>
        </h1>

        {/* Subtitle */}
        <p className="dashboard-subtitle">
          Welcome, {user?.name || "User"}! Your intelligent legal assistant.
        </p>

        {/* Buttons */}
        <div className="button-container">

          <button
            className="dashboard-button btn-agent"
            onClick={() => navigate("/agent")}
          >
            <span className="btn-icon">🤖</span>
            <span className="btn-text">
              <span className="btn-label">AI Agent (Unified)</span>
              <span className="btn-desc">One interface for all services</span>
            </span>
            <span className="btn-arrow">→</span>
          </button>

          <button
            className="dashboard-button btn-chat"
            onClick={() => navigate("/chat")}
          >
            <span className="btn-icon">🤖</span>
            <span className="btn-text">
              <span className="btn-label">Chat Bot</span>
              <span className="btn-desc">Ask any legal question instantly</span>
            </span>
            <span className="btn-arrow">→</span>
          </button>

          <button
            className="dashboard-button btn-complaint"
            onClick={() => navigate("/complaint")}
          >
            <span className="btn-icon">📄</span>
            <span className="btn-text">
              <span className="btn-label">Complaint Generator</span>
              <span className="btn-desc">Draft a formal complaint letter</span>
            </span>
            <span className="btn-arrow">→</span>
          </button>

          <button
            className="dashboard-button btn-judgment"
            onClick={() => navigate("/judgment")}
          >
            <span className="btn-icon">⚖️</span>
            <span className="btn-text">
              <span className="btn-label">Judgment Search</span>
              <span className="btn-desc">Find similar legal cases</span>
            </span>
            <span className="btn-arrow">→</span>
          </button>

          <button
            className="dashboard-button btn-advocates"
            onClick={() => navigate("/advocates")}
          >
            <span className="btn-icon">👨‍⚖️</span>
            <span className="btn-text">
              <span className="btn-label">Find Advocates</span>
              <span className="btn-desc">Browse lawyers by district</span>
            </span>
            <span className="btn-arrow">→</span>
          </button>

        </div>

        {/* Footer */}
        <p className="dashboard-footer">
          🔒 Secure & Confidential · Powered by AI
        </p>
        <button onClick={handleLogout} className="logout-footer-btn">Logout</button>
      <span className="deco-scales">⚖️</span>
      </div>
    
  );
}

export default Dashboard;