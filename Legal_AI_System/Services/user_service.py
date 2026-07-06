import json
import os
from datetime import datetime
import hashlib

class UserService:
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(__file__), "..", "Pipeline", "users.json")
        self.load_users()
    
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, email, password, name, phone, address, district=None):
        if email in self.users:
            return {"success": False, "message": "User already exists"}
        
        self.users[email] = {
            "password": self.hash_password(password),
            "name": name,
            "phone": phone,
            "address": address,
            "district": district,
            "created_at": datetime.now().isoformat()
        }
        self.save_users()
        return {"success": True, "message": "Registration successful"}
    
    def login(self, email, password):
        if email not in self.users:
            return {"success": False, "message": "User not found"}
        
        if self.users[email]["password"] != self.hash_password(password):
            return {"success": False, "message": "Invalid password"}
        
        return {"success": True, "user": self.get_user_profile(email)}
    
    def get_user_profile(self, email):
        if email not in self.users:
            return None
        
        user = self.users[email].copy()
        user.pop("password")
        user["email"] = email
        return user
    
    def update_profile(self, email, **kwargs):
        if email not in self.users:
            return {"success": False, "message": "User not found"}
        
        for key, value in kwargs.items():
            if key != "password" and key in ["name", "phone", "address", "district"]:
                self.users[email][key] = value
        
        self.save_users()
        return {"success": True, "message": "Profile updated"}
