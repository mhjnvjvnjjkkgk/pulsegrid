# ============================================================
# PulseGrid E2E Test Suite - Triage & Unified Search API Tests
# ============================================================

import pytest
import sys
import os

# Add parent directory to python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client


class TestTriageAPI:
    """Tests for symptom triage classification and language support."""

    def test_red_cardiac_symptom_english(self, client):
        response = client.post('/api/triage', json={'text': 'severe chest pain radiating to left arm'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['severity'] == 'RED'
        assert data['recommended_ward'] == 'cardiac_icu'

    def test_red_symptom_hinglish(self, client):
        response = client.post('/api/triage', json={'text': 'chhati me bahut dard ho raha hai'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['severity'] == 'RED'
        assert data['recommended_ward'] == 'cardiac_icu'

    def test_red_symptom_benglish(self, client):
        response = client.post('/api/triage', json={'text': 'bukey khub byatha korchhe'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['severity'] == 'RED'
        assert data['recommended_ward'] == 'cardiac_icu'

    def test_yellow_symptom(self, client):
        response = client.post('/api/triage', json={'text': 'pet me bahut dard hai'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['severity'] == 'YELLOW'
        assert data['recommended_ward'] == 'general_ward'

    def test_green_symptom(self, client):
        response = client.post('/api/triage', json={'text': 'mild headache since morning'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['severity'] == 'GREEN'


class TestBloodSearchAPI:
    """Tests for blood group term detection and search matching."""

    def test_blood_search_o_negative(self, client):
        response = client.post('/api/search', json={'text': 'need O negative blood urgently'})
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('is_blood_query') is True
        assert data.get('blood_group') == 'O-'
        assert 'blood_matches' in data

    def test_blood_search_a_positive(self, client):
        response = client.post('/api/search', json={'text': 'A+ blood needed for surgery'})
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('is_blood_query') is True
        assert data.get('blood_group') == 'A+'

    def test_blood_search_b_positive(self, client):
        response = client.post('/api/search', json={'text': 'B positive platelets required'})
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('is_blood_query') is True
        assert data.get('blood_group') == 'B+'

    def test_blood_search_ab_negative(self, client):
        response = client.post('/api/search', json={'text': 'AB- blood required'})
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('is_blood_query') is True
        assert data.get('blood_group') == 'AB-'


class TestUnifiedSearchEndpoint:
    """Tests for unified search endpoint handling symptoms and blood requests."""

    def test_unified_search_symptoms_and_hospitals(self, client):
        response = client.post('/api/search', json={'text': 'chest pain', 'lat': 22.5392, 'lng': 88.3433})
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] is True
        assert data['severity'] == 'RED'
        assert data['recommended_ward'] == 'cardiac_icu'
        assert isinstance(data['recommended_hospitals'], list)
        assert len(data['recommended_hospitals']) > 0

    def test_unified_search_missing_text_returns_400(self, client):
        response = client.post('/api/search', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
