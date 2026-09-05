import unittest
import json
import re
from app import app
from triage_service import classify_symptoms, parse_blood_search

class TestMilestone1Backend(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_blood_group_regex_parsing(self):
        """Test regex parsing for various blood group queries."""
        regex = re.compile(r'\b(O|A|B|AB)\s*([\+\-]|positive|negative)(?:\b|\s|$)', re.IGNORECASE)
        
        test_cases = [
            ("O- negative blood needed", "O-"),
            ("We need A+ blood urgently", "A+"),
            ("AB negative blood required", "AB-"),
            ("B positive blood donor", "B+"),
            ("O negative", "O-"),
            ("A positive", "A+"),
        ]

        for query, expected in test_cases:
            match = regex.search(query)
            self.assertIsNotNone(match, f"Regex failed to match: {query}")
            parsed = parse_blood_search(query)
            self.assertEqual(parsed, expected, f"Expected {expected} for query '{query}', got {parsed}")

    def test_classify_symptoms_with_blood(self):
        """Test classify_symptoms function returns is_blood_request=True for blood queries."""
        res = classify_symptoms("Need O- negative blood urgently")
        self.assertTrue(res["is_blood_request"])
        self.assertEqual(res["blood_group"], "O-")
        self.assertIn("Blood Request (O-)", res["ward"])

    def test_api_search_endpoint(self):
        """Test POST /api/search endpoint with symptom and blood query."""
        response = self.app.post('/api/search',
                                 data=json.dumps({"text": "O- negative blood needed"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("is_blood_query"))
        self.assertEqual(data.get("blood_group"), "O-")
        self.assertIn("hospitals", data)

    def test_api_triage_symptoms(self):
        """Test POST /api/triage endpoint with severe symptom."""
        response = self.app.post('/api/triage',
                                 data=json.dumps({"text": "severe chest pain"}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("severity"), "RED")
        self.assertEqual(data.get("recommended_ward"), "cardiac_icu")

if __name__ == '__main__':
    unittest.main()
