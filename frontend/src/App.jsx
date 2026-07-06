import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ChatBot from "./pages/ChatBot";
import Complaint from "./pages/Complaint";
import Judgment from "./pages/Judgment";
import Agent from "./pages/Agent";
import Auth from "./pages/Auth";
import JudgmentDetail from "./pages/JudgmentDetail";
import Advocates from "./pages/Advocates";

function ProtectedRoute({ children }) {
  const user = localStorage.getItem("user");
  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Auth />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><ChatBot /></ProtectedRoute>} />
        <Route path="/complaint" element={<ProtectedRoute><Complaint /></ProtectedRoute>} />
        <Route path="/judgment" element={<ProtectedRoute><Judgment /></ProtectedRoute>} />
        <Route path="/agent" element={<ProtectedRoute><Agent /></ProtectedRoute>} />
        <Route path="/judgment-detail" element={<ProtectedRoute><JudgmentDetail /></ProtectedRoute>} />
        <Route path="/advocates" element={<ProtectedRoute><Advocates /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}

export default App;