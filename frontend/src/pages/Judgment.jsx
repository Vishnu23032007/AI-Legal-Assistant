import { useState } from "react";
import API from "../services/api";
import "./Judgment.css";

function Judgment() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await API.post("/judgment", { query, top_n: 5 });
      setResults(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to retrieve judgments");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="judgment-container">
      <div className="judgment-header">
        <h1>⚖️ Judgment Search</h1>
        <p>Find similar legal cases based on your query</p>
      </div>

      <div className="search-box">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your legal case or query..."
          rows="4"
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? "Searching..." : "🔍 Search Cases"}
        </button>
      </div>

      {results && (
        <div className="results-container">
          <div className="results-header">
            <h2>📚 Found {results.total_results} Similar Cases</h2>
          </div>

          {results.cases.map((caseItem) => (
            <div key={caseItem.rank} className="case-card">
              <div className="case-header">
                <span className="case-rank">#{caseItem.rank}</span>
                <span className="case-similarity">{caseItem.similarity}% Match</span>
                <span className={`case-outcome outcome-${caseItem.outcome.toLowerCase()}`}>
                  {caseItem.outcome}
                </span>
              </div>

              <h3 className="case-title">{caseItem.case_title}</h3>

              <div className="case-meta">
                <span>📅 {caseItem.year}</span>
                <span>📄 {caseItem.page_count} pages</span>
                <span>📝 {caseItem.word_count} words</span>
              </div>

              <div className="case-parties">
                <div>
                  <strong>Petitioner:</strong> {caseItem.petitioner}
                </div>
                <div>
                  <strong>Respondent:</strong> {caseItem.respondent}
                </div>
              </div>

              <div className="case-citation">
                <strong>Citation:</strong> {caseItem.citation}
              </div>

              <div className="case-sections">
                <div className="case-section">
                  <h4>📋 Background</h4>
                  <p>{caseItem.background}</p>
                </div>

                <div className="case-section">
                  <h4>⚔️ Arguments</h4>
                  <p>{caseItem.arguments}</p>
                </div>

                <div className="case-section">
                  <h4>⚖️ Judgment</h4>
                  <p>{caseItem.judgment}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Judgment;
