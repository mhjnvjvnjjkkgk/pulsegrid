# ============================================================
# PulseGrid Unit & Integration Test Suite - Holds Bed Reservation Engine
# Milestone 2 Tests for R2 Requirements
# ============================================================

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app
import database


@pytest.fixture(autouse=True)
def reset_mock_state():
    """Reset mock database state before each test."""
    database.MOCK_HOLDS.clear()
    for h in database.MOCK_HOSPITALS:
        h['adult_icu_held'] = 1
        h['pediatric_icu_held'] = 1
        h['cardiac_icu_held'] = 1
        h['general_ward_held'] = 5
        h['adult_icu_occupied'] = 20
        h['pediatric_icu_occupied'] = 10
        h['cardiac_icu_occupied'] = 10
        h['general_ward_occupied'] = 100

@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client


class TestHoldsEngine:
    """Comprehensive tests for Soft/Hard-Lock Bed Reservation Engine (Milestone 2)."""

    def test_soft_lock_creation_decrements_bed_immediately(self, client):
        """Test that POST /api/holds/create reserves 1 bed immediately and returns otp_code and bed_count."""
        hospitals = database.get_all_hospitals()
        hospital = hospitals[0]
        h_id = hospital['id']
        res_type = 'general_ward'

        total = database._safe_int(hospital.get(f"{res_type}_total"))
        occupied = database._safe_int(hospital.get(f"{res_type}_occupied"))
        held_before = database._safe_int(hospital.get(f"{res_type}_held"))
        available_before = total - occupied - held_before

        payload = {
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'YELLOW'
        }
        res = client.post('/api/holds/create', json=payload)
        assert res.status_code == 201
        data = res.get_json()

        assert data.get('success') is True or data.get('ok') is True
        assert 'hold_id' in data
        assert 'otp_code' in data
        otp = str(data['otp_code'])
        assert len(otp) == 4 and otp.isdigit()
        assert 'expires_at' in data
        assert data.get('bed_count') == available_before - 1

        # Confirm in database
        h_after = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_after = database._safe_int(h_after.get(f"{res_type}_held"))
        assert held_after == held_before + 1

    def test_paramedic_hold_duration_20_mins(self, client):
        """Test paramedic hold type receives 20-minute expiry."""
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']

        res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': 'adult_icu',
            'hold_type': 'PARAMEDIC',
            'phone': '9876543210',
            'severity': 'RED'
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data.get('minutes') == 20 or data.get('seconds_left') == 1200

    def test_manual_cancel_restores_bed_count(self, client):
        """Test POST /api/holds/cancel restores bed count to available pool."""
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        res_type = 'cardiac_icu'

        h_before = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_before = database._safe_int(h_before.get(f"{res_type}_held"))

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9998887776',
            'severity': 'YELLOW'
        })
        hold_data = create_res.get_json()
        hold_id = hold_data['hold_id']

        # Cancel hold
        cancel_res = client.post('/api/holds/cancel', json={
            'hold_id': hold_id,
            'phone': '9998887776'
        })
        assert cancel_res.status_code == 200
        cancel_data = cancel_res.get_json()
        assert cancel_data.get('status') == 'CANCELLED'
        assert 'bed_count' in cancel_data

        # Verify bed count restored
        h_after = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_after = database._safe_int(h_after.get(f"{res_type}_held"))
        assert held_after == held_before

    def test_location_update_vector_toward_and_away(self, client):
        """Test GPS location update vector tracking (TOWARD, AWAY, auto-cancel after 3 wrong directions)."""
        hospitals = database.get_all_hospitals()
        sskm = next(h for h in hospitals if 'SSKM' in h['name'])
        h_id = sskm['id']

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': 'cardiac_icu',
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'RED'
        })
        hold_id = create_res.get_json()['hold_id']

        # 1. Initial stationary update
        u1 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5500,
            'user_lng': 88.3500
        }).get_json()
        assert u1['movement_direction'] == 'STATIONARY'

        # 2. Move TOWARD SSKM (SSKM lat: 22.5392, lng: 88.3433)
        u2 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5400,
            'user_lng': 88.3440
        }).get_json()
        assert u2['movement_direction'] == 'TOWARD'
        assert u2['wrong_direction_count'] == 0

        # 3. Move AWAY (3 times -> Auto-cancel)
        w1 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5600,
            'user_lng': 88.3600
        }).get_json()
        assert w1['movement_direction'] == 'AWAY'
        assert w1['wrong_direction_count'] == 1

        w2 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5800,
            'user_lng': 88.3800
        }).get_json()
        assert w2['wrong_direction_count'] == 2

        w3 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.6000,
            'user_lng': 88.4000
        }).get_json()
        assert w3['status'] == 'CANCELLED'
        assert w3['auto_cancelled'] is True
        assert 'bed_count' in w3

    def test_hard_lock_otp_redemption_converts_to_permanent_claim(self, client):
        """Test POST /api/holds/redeem with valid OTP converts soft lock to REDEEMED permanent bed claim."""
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        res_type = 'general_ward'

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'YELLOW'
        })
        hold_data = create_res.get_json()
        hold_id = hold_data['hold_id']
        otp = hold_data['otp_code']

        redeem_res = client.post('/api/holds/redeem', json={
            'hospital_id': h_id,
            'hold_id': hold_id,
            'otp_code': otp
        })
        assert redeem_res.status_code == 200
        r_data = redeem_res.get_json()
        assert r_data.get('status') == 'REDEEMED'

        # Verify hold status in database
        hold_db = database.get_hold_by_id(hold_id)
        assert hold_db['status'] == 'REDEEMED'

    def test_invalid_otp_redemption_returns_400(self, client):
        """Test redeeming with invalid OTP returns 400 error."""
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']

        res = client.post('/api/holds/redeem', json={
            'hospital_id': h_id,
            'otp_code': '0000'
        })
        assert res.status_code == 400
        assert 'error' in res.get_json()
