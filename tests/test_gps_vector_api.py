# ============================================================
# PulseGrid E2E Test Suite - GPS Vector & Auto-Cancel Engine API Tests
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


class TestGPSVectorAPI:
    """Tests for GPS updates, movement vector logic (TOWARD, STATIONARY, AWAY), wrong direction tracking, and auto-cancellation."""

    def test_gps_update_toward_resets_wrong_direction_count(self, client):
        # 1. Create a hold at SSKM Hospital (lat: 22.5392, lng: 88.3433)
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

        # 2. Initial position update (e.g. 2 km away)
        loc1 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5550,
            'user_lng': 88.3550
        })
        assert loc1.status_code == 200
        d1 = loc1.get_json()
        assert d1['status'] == 'ACTIVE'
        assert d1['movement_direction'] == 'STATIONARY'
        assert d1['wrong_direction_count'] == 0

        # 3. Move closer to SSKM (TOWARD)
        loc2 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5410,
            'user_lng': 88.3440
        })
        assert loc2.status_code == 200
        d2 = loc2.get_json()
        assert d2['status'] == 'ACTIVE'
        assert d2['movement_direction'] == 'TOWARD'
        assert d2['wrong_direction_count'] == 0

    def test_gps_update_away_increments_wrong_direction_count(self, client):
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': 'adult_icu',
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'RED'
        })
        hold_id = create_res.get_json()['hold_id']

        # Update 1: initial position
        client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5400,
            'user_lng': 88.3400
        })

        # Update 2: move away
        loc_away = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5700,
            'user_lng': 88.3700
        })
        assert loc_away.status_code == 200
        d = loc_away.get_json()
        assert d['movement_direction'] == 'AWAY'
        assert d['wrong_direction_count'] == 1

    def test_three_wrong_directions_trigger_auto_cancellation(self, client):
        # 1. Create a hold
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        res_type = 'cardiac_icu'

        h_before = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_before = database._safe_int(h_before.get(f"{res_type}_held"))

        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'RED'
        })
        hold_id = create_res.get_json()['hold_id']

        # 2. Position 0 (initial)
        client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5400,
            'user_lng': 88.3400
        })

        # 3. Position 1 (AWAY #1)
        r1 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5600,
            'user_lng': 88.3600
        }).get_json()
        assert r1['wrong_direction_count'] == 1
        assert r1['status'] == 'ACTIVE'

        # 4. Position 2 (AWAY #2)
        r2 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5800,
            'user_lng': 88.3800
        }).get_json()
        assert r2['wrong_direction_count'] == 2
        assert r2['status'] == 'ACTIVE'

        # 5. Position 3 (AWAY #3 -> Auto-Cancel Trigger!)
        r3 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.6000,
            'user_lng': 88.4000
        }).get_json()

        assert r3['status'] == 'CANCELLED'
        assert r3['auto_cancelled'] is True
        assert r3['wrong_direction_count'] == 3

        # 6. Check database: hold status is CANCELLED and bed returned to pool
        hold_info = database.get_hold_by_id(hold_id)
        assert hold_info['status'] == 'CANCELLED'

        h_after = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        held_after = database._safe_int(h_after.get(f"{res_type}_held"))
        assert held_after == held_before
