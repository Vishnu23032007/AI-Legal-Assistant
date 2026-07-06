import json
import os

class AdvocateService:
    def __init__(self):
        self.advocates_file = os.path.join(os.path.dirname(__file__), "..", "Pipeline", "tamilnadu_lawyers_dataset.json")
        self.load_advocates()
    
    def load_advocates(self):
        with open(self.advocates_file, 'r', encoding='utf-8') as f:
            self.advocates = json.load(f)
    
    def get_advocates_by_district(self, district, limit=5):
        """Get advocates from a specific district"""
        filtered = [adv for adv in self.advocates if adv['city'].lower() == district.lower()]
        return filtered[:limit]
    
    def match_advocates(self, district, scenario_text, limit=3):
        """Match advocates based on district and scenario keywords"""
        # Get advocates from user's district
        district_advocates = [adv for adv in self.advocates if adv['city'].lower() == district.lower()]
        
        if not district_advocates:
            return []
        
        # Keywords mapping to practice areas
        keywords_map = {
            'divorce': ['Divorce', 'Family Law', 'Family'],
            'family': ['Family Law', 'Family', 'Divorce', 'Child Custody'],
            'property': ['Property Law', 'Property', 'Landlord/Tenant', 'RERA'],
            'criminal': ['Criminal Defense', 'Criminal', 'Anticipatory Bail'],
            'cheque': ['Banking & Finance', 'Cheque Bounce', 'Recovery'],
            'consumer': ['Consumer Law', 'Consumer Court'],
            'labour': ['Labour & Civil Matters', 'Labour & Service'],
            'corporate': ['Corporate Law', 'Corporate', 'Documentation'],
            'accident': ['Motor Accident', 'Personal Injury', 'Insurance'],
            'domestic violence': ['Domestic Violence', 'Women', 'Family Law'],
            'dowry': ['Dowry Case', 'Family Law', 'Women'],
            'cyber': ['Cyber Crime', 'Criminal Defense'],
            'fraud': ['Fraud Case', 'Criminal Defense'],
        }
        
        # Find matching practice areas
        scenario_lower = scenario_text.lower()
        relevant_areas = set()
        
        for keyword, areas in keywords_map.items():
            if keyword in scenario_lower:
                relevant_areas.update(areas)
        
        # If no specific match, use general areas
        if not relevant_areas:
            relevant_areas = {'Civil', 'Criminal Defense', 'Family Law'}
        
        # Score advocates based on matching practice areas
        scored_advocates = []
        for adv in district_advocates:
            score = sum(1 for area in adv['practice_areas'] if area in relevant_areas)
            if score > 0:
                scored_advocates.append({
                    'name': adv['name'],
                    'city': adv['city'],
                    'profile': adv['profile'],
                    'practice_areas': adv['practice_areas'][:5],
                    'match_score': score
                })
        
        # Sort by score and return top matches
        scored_advocates.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_advocates[:limit]
