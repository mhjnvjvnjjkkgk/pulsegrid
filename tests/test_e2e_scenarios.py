# ============================================================
# PulseGrid E2E Test Suite - End-to-End User Scenarios (Tiers 1-4)
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


class TestE2EScenarios:
    """Complete end-to-end real-world user flows simulating citizen, paramedic, and hospital nurse actions."""

    def test_scenario_a_cardiac_emergency_critical_path(self, client):
        """
        Scenario A:
        1. Hinglish symptom triage input ("chhati me tez dard").
        2. Triage output: RED, cardiac_icu, recommended hospitals.
        3. Bed soft lock creation (bed count decrements, 4-digit OTP generated, 15m countdown).
        4. Patient streams GPS location TOWARD hospital.
        5. Nurse inputs OTP at desk -> Hard lock bed redemption, patient admitted.
        """
        # Step 1 & 2: Triage & Facility Search
        search_res = client.post('/api/search', json={
            'text': 'chhati me tez dard ho raha hai',
            'lat': 22.5392,
            'lng': 88.3433
        })
        assert search_res.status_code == 200
        search_data = search_res.get_json()
        assert search_data['severity'] == 'RED'
        assert search_data['recommended_ward'] == 'cardiac_icu'
        hospitals = search_data['recommended_hospitals']
        assert len(hospitals) > 0
        target_hospital = hospitals[0]
        h_id = target_hospital['id']

        # Check bed count before hold
        res_type = 'cardiac_icu'
        total = database._safe_int(target_hospital.get(f"{res_type}_total"))
        occupied = database._safe_int(target_hospital.get(f"{res_type}_occupied"))
        held_before = database._safe_int(target_hospital.get(f"{res_type}_held"))
        avail_before = total - occupied - held_before

        # Step 3: Bed Soft Lock Creation
        create_res = client.post('/api/holds/create', json={
            'hospital_id': h_id,
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9876543210',
            'severity': 'RED'
        })
        assert create_res.status_code == 201
        hold_info = create_res.get_json()
        assert hold_info['status'] == 'ACTIVE'
        otp = hold_info.get('otp_code') or hold_info.get('otp')
        hold_id = hold_info['hold_id']
        assert hold_info['bed_count'] == avail_before - 1

        # Step 4: Stream GPS Location TOWARD Hospital
        loc_res1 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5500,
            'user_lng': 88.3500
        })
        assert loc_res1.get_json()['status'] == 'ACTIVE'

        loc_res2 = client.post('/api/holds/location_update', json={
            'hold_id': hold_id,
            'user_lat': 22.5400,
            'user_lng': 88.3440
        })
        loc_data2 = loc_res2.get_json()
        assert loc_data2['status'] == 'ACTIVE'
        assert loc_data2['movement_direction'] == 'TOWARD'

        # Step 5: Nurse redeems OTP at hospital desk
        redeem_res = client.post('/api/holds/redeem', json={
            'hospital_id': h_id,
            'hold_id': hold_id,
            'otp_code': otp
        })
        assert redeem_res.status_code == 200
        redeem_data = redeem_res.get_json()
        assert redeem_data['status'] == 'REDEEMED'

        # Verify final state
        h_final = next(h for h in database.get_all_hospitals() if h['id'] == h_id)
        occ_final = database._safe_int(h_final.get(f"{res_type}_occupied"))
        assert occ_final == occupied + 1

    def test_scenario_b_wrong_direction_auto_cancel_and_rebooking(self, client):
        """
        Scenario B:
        1. Patient locks a bed at Hospital 1.
        2. Patient strays off course 3 times (AWAY vector).
        3. System auto-cancels soft lock and releases bed count back to pool.
        4. Patient creates a new hold at Hospital 2.
        """
        hospitals = database.get_all_hospitals()
        h1 = hospitals[0]
        h2 = hospitals[1]
        res_type = 'adult_icu'

        # Step 1: Create Hold at Hospital 1
        c1 = client.post('/api/holds/create', json={
            'hospital_id': h1['id'],
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9123456789',
            'severity': 'RED'
        }).get_json()
        h1_hold_id = c1['hold_id']

        # Step 2: Stray off course 3 times
        client.post('/api/holds/location_update', json={'hold_id': h1_hold_id, 'user_lat': 22.5000, 'user_lng': 88.3000})
        client.post('/api/holds/location_update', json={'hold_id': h1_hold_id, 'user_lat': 22.5200, 'user_lng': 88.2800})
        client.post('/api/holds/location_update', json={'hold_id': h1_hold_id, 'user_lat': 22.5400, 'user_lng': 88.2600})
        r_cancel = client.post('/api/holds/location_update', json={'hold_id': h1_hold_id, 'user_lat': 22.5600, 'user_lng': 88.2400}).get_json()

        # Step 3: Verify auto-cancellation
        assert r_cancel['status'] == 'CANCELLED'
        assert r_cancel['auto_cancelled'] is True

        # Step 4: Re-book at Hospital 2
        c2 = client.post('/api/holds/create', json={
            'hospital_id': h2['id'],
            'resource_type': res_type,
            'hold_type': 'CITIZEN',
            'phone': '9123456789',
            'severity': 'RED'
        })
        assert c2.status_code == 201
        assert c2.get_json()['status'] == 'ACTIVE'

    def test_scenario_c_blood_emergency_paramedic_flow(self, client):
        """
        Scenario C:
        1. Paramedic searches for emergency blood ("O negative").
        2. System returns matching blood inventory.
        3. Paramedic soft-locks bed at matching hospital.
        """
        search_res = client.post('/api/search', json={'text': 'need O negative blood for trauma patient'})
        assert search_res.status_code == 200
        search_data = search_res.get_json()

        assert search_data['is_blood_query'] is True
        assert search_data['blood_group'] == 'O-'

        hospitals = search_data['recommended_hospitals']
        target_h = hospitals[0]

        create_res = client.post('/api/holds/create', json={
            'hospital_id': target_h['id'],
            'resource_type': 'adult_icu',
            'hold_type': 'PARAMEDIC',
            'phone': '9998887776',
            'severity': 'RED'
        })
        assert create_res.status_code == 201
        assert create_res.get_json()['hold_type'] == 'PARAMEDIC'

    def test_scenario_d_nurse_quick_counter_adjustment(self, client):
        """
        Scenario D:
        1. Hospital desk nurse taps [+] on occupied counter.
        2. Occupied bed count increments by 1.
        3. Nurse taps [-] on occupied counter.
        4. Occupied bed count decrements by 1.
        """
        hospitals = database.get_all_hospitals()
        h_id = hospitals[0]['id']
        ward = 'adult_icu'
        initial_occ = database._safe_int(hospitals[0].get(f"{ward}_occupied"))

        # Nurse taps [+]
        inc_res = client.post('/api/hospital/counter', json={
            'hospital_id': h_id,
            'ward': ward,
            'delta': 1
        })
        assert inc_res.status_code == 200
        inc_data = inc_res.get_json()
        assert inc_data['new_occupied'] == initial_occ + 1

        # Nurse taps [-]
        dec_res = client.post('/api/hospital/counter', json={
            'hospital_id': h_id,
            'ward': ward,
            'delta': -1
        })
        assert dec_res.status_code == 200
        dec_data = dec_res.get_json()
        assert dec_data['new_occupied'] == initial_occ
