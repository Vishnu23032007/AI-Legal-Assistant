import { useNavigate } from "react-router-dom";

function LanguageSelect() {
  const navigate = useNavigate();

  const selectLanguage = (lang) => {
    localStorage.setItem("app_language", lang); // store globally
    navigate("/chatbot"); // go to chatbot page
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h2>Select Your Preferred Language</h2>

      <button onClick={() => selectLanguage("english")}>
        English
      </button>

      <button onClick={() => selectLanguage("tamil")}>
        தமிழ்
      </button>
    </div>
  );
}

export default LanguageSelect;