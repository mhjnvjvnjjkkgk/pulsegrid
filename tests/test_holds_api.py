# ============================================================
# PulseGrid E2E Test Suite - Holds & Lock Engine API Tests
# ============================================================

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app
import database


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client


class TestHoldsAPI:
    """Tests for soft-lock creation, OTP generation, redemption, and cancellation."""

    def test_create_soft_lock_decrements_bed_count(self, client):
        # 1. Pick hospital and check initial bed availability
        hospitals = database.get_all_hospitals()
        hospital = hospitals[0]
        h_id = hospital['id']
        res_type = 'cardiac_icu'

        # Get initial available beds
        total = database._safe_int(hospital.get(f"{res_type}_total"))
        occupied = database._safe_int(hospital.get(f"{res_type}_occupied"))
        held_before = database._safe_int(hospital.get(f"{res_type}_held"))
        available_before = total - occupied - held_before

        # 2. Request soft-lock creation
        payload = {
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'RED'
        }
        res = client.post('/api/holds/create', json=payload)
        assert res.status_code == 201
        data = res.get_json()

        assert data.get('success') is True or data.get('ok') is True
        assert 'hold_id' in data
        assert 'otp_code' in data or 'otp' in data
        otp = data.get('otp_code') or data.get('otp')
        assert len(str(otp)) == 4
        assert 'expires_at' in data

        # Check bed count decremented
        assert data.get('bed_count') == available_before - 1

        # Confirm in database
        h_after = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_after = database._safe_int(h_after.get(f"{res_type}_held"))
        assert held_after == held_before + 1

    def test_redeem_hard_lock_success(self, client):
        # 1. Create a hold
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        res_type = 'cardiac_icu'

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'RED'
        })
        hold_data = create_res.get_json()
        otp = hold_data.get('otp_code') or hold_data.get('otp')
        hold_id = hold_data['hold_id']

        # 2. Redeem hard lock with valid OTP
        redeem_res = client.post('/api/holds/redeem', json={
            'hospital_id': h_id,
            'hold_id': hold_id,
            'otp_code': otp
        })
        assert redeem_res.status_code == 200
        data = redeem_res.get_json()
        assert data.get('success') is True or data.get('ok') is True
        assert data.get('status') == 'REDEEMED'

        # 3. Verify hold status in database is REDEEMED
        info = database.get_hold_by_id(hold_id)
        assert info.get('status') == 'REDEEMED'

    def test_manual_cancellation_restores_bed_count(self, client):
        # 1. Create a hold
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        res_type = 'adult_icu'

        h_before = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_before = database._safe_int(h_before.get(f"{res_type}_held"))

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543211',
            'severity': 'RED'
        })
        hold_data = create_res.get_json()
        hold_id = hold_data['hold_id']

        # 2. Cancel hold manually
        cancel_res = client.post('/api/holds/cancel', json={
            'hold_id': hold_id,
            'phone': '9876543211'
        })
        assert cancel_res.status_code == 200
        cancel_data = cancel_res.get_json()
        assert cancel_data.get('status') == 'CANCELLED'

        # 3. Verify held count returned to original
        h_after = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_after = database._safe_int(h_after.get(f"{res_type}_held"))
        assert held_after == held_before

    def test_invalid_otp_redemption_fails(self, client):
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        res = client.post('/api/holds/redeem', json={
            'hospital_id': h_id,
            'otp_code': '0000'
        })
        assert res.status_code == 400
        assert 'error' in res.get_json()
