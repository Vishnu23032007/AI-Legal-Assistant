import { useLocation, useNavigate } from "react-router-dom";
import "./JudgmentDetail.css";

function JudgmentDetail() {
  const location = useLocation();
  const navigate = useNavigate();
  const judgment = location.state?.judgment;

  if (!judgment) {
    return (
      <div className="judgment-detail-container">
        <p>No judgment data available.</p>
        <button onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  return (
    <div className="judgment-detail-container">
      <button onClick={() => navigate(-1)} className="back-btn">
        ← Back to Analysis
      </button>

      <div className="judgment-detail-card">
        <div className="judgment-detail-header">
          <h1>{judgment.case_title}</h1>
          <div className="header-badges">
            <span className="year-badge">📅 {judgment.year}</span>
            <span className={`outcome-badge-large outcome-${judgment.outcome.toLowerCase()}`}>
              {judgment.outcome}
            </span>
            <span className="similarity-badge-large">{judgment.similarity}% Match</span>
          </div>
        </div>

        <div className="judgment-section">
          <h2>📋 Case Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <strong>Petitioner:</strong>
              <p>{judgment.petitioner}</p>
            </div>
            <div className="info-item">
              <strong>Respondent:</strong>
              <p>{judgment.respondent}</p>
            </div>
            <div className="info-item">
              <strong>Citation:</strong>
              <p>{judgment.citation}</p>
            </div>
            <div className="info-item">
              <strong>Pages:</strong>
              <p>{judgment.page_count} pages</p>
            </div>
            <div className="info-item">
              <strong>Word Count:</strong>
              <p>{judgment.word_count} words</p>
            </div>
          </div>
        </div>

        <div className="judgment-section">
          <h2>📖 Background</h2>
          <p className="section-content">{judgment.background}</p>
        </div>

        <div className="judgment-section">
          <h2>⚔️ Arguments</h2>
          <p className="section-content">{judgment.arguments}</p>
        </div>

        <div className="judgment-section">
          <h2>⚖️ Judgment</h2>
          <p className="section-content">{judgment.judgment}</p>
        </div>
      </div>
    </div>
  );
}

export default JudgmentDetail;
