import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "./Auth.css";

function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
    phone: "",
    address: "",
    district: ""
  });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const endpoint = isLogin ? "/login" : "/register";
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;
      
      const response = await API.post(endpoint, payload);
      
      if (response.data.success) {
        if (isLogin) {
          localStorage.setItem("user", JSON.stringify(response.data.user));
          navigate("/");
        } else {
          alert("Registration successful! Please login.");
          setIsLogin(true);
        }
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      alert("Error: " + (error.response?.data?.message || error.message));
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>⚖️ LAW SAKTHI</h1>
        <h2>{isLogin ? "Login" : "Register"}</h2>
        
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <input
                type="text"
                placeholder="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
              <input
                type="tel"
                placeholder="Phone Number"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                required
              />
              <textarea
                placeholder="Address"
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                required
              />
              <select
                value={formData.district}
                onChange={(e) => setFormData({...formData, district: e.target.value})}
                required
              >
                <option value="">Select District</option>
                <option value="chennai">Chennai</option>
                <option value="coimbatore">Coimbatore</option>
                <option value="madurai">Madurai</option>
                <option value="salem">Salem</option>
                <option value="erode">Erode</option>
                <option value="vellore">Vellore</option>
                <option value="tirunelveli">Tirunelveli</option>
                <option value="thoothukudi">Thoothukudi</option>
                <option value="thanjavur">Thanjavur</option>
                <option value="dindigul">Dindigul</option>
                <option value="nagapattinam">Nagapattinam</option>
              </select>
            </>
          )}
          
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
          
          <button type="submit">{isLogin ? "Login" : "Register"}</button>
        </form>
        
        <p className="toggle-text">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? "Register" : "Login"}
          </span>
        </p>
      </div>
    </div>
  );
}

export default Auth;
