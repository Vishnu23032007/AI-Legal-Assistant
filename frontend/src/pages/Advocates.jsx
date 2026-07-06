import { useState, useEffect } from "react";
import advocatesData from "../../../Legal_AI_System/Pipeline/tamilnadu_lawyers_dataset.json";
import "./Advocates.css";

function Advocates() {
  const [selectedCity, setSelectedCity] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredAdvocates, setFilteredAdvocates] = useState([]);

  const cities = ["all", ...new Set(advocatesData.map(adv => adv.city))];

  useEffect(() => {
    let filtered = advocatesData;

    if (selectedCity !== "all") {
      filtered = filtered.filter(adv => adv.city === selectedCity);
    }

    if (searchQuery) {
      filtered = filtered.filter(adv =>
        adv.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        adv.practice_areas.some(area => area.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    setFilteredAdvocates(filtered);
  }, [selectedCity, searchQuery]);

  return (
    <div className="advocates-container">
      <div className="advocates-header">
        <h1>⚖️ Find Legal Advocates</h1>
        <p>Browse advocates by district and practice area</p>
      </div>

      <div className="advocates-filters">
        <select
          value={selectedCity}
          onChange={(e) => setSelectedCity(e.target.value)}
          className="city-select"
        >
          {cities.map(city => (
            <option key={city} value={city}>
              {city === "all" ? "All Districts" : city.charAt(0).toUpperCase() + city.slice(1)}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Search by name or practice area..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="advocates-count">
        Showing {filteredAdvocates.length} advocate(s)
      </div>

      <div className="advocates-grid">
        {filteredAdvocates.map((advocate, index) => (
          <div key={index} className="advocate-card">
            <div className="advocate-header">
              <h3>{advocate.name}</h3>
              <span className="advocate-city">{advocate.city.toUpperCase()}</span>
            </div>
            <div className="advocate-areas">
              {advocate.practice_areas.slice(0, 5).map((area, idx) => (
                <span key={idx} className="practice-area">{area}</span>
              ))}
              {advocate.practice_areas.length > 5 && (
                <span className="practice-area more">+{advocate.practice_areas.length - 5} more</span>
              )}
            </div>
            <a
              href={advocate.profile}
              target="_blank"
              rel="noopener noreferrer"
              className="profile-link"
            >
              View Profile →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Advocates;
