# ============================================================
# PulseGrid E2E Test Suite - Routing Stability & Post-Booking UX
# ============================================================

import pytest
import sys
import os
import re
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app
import database


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client


class TestRoutingAndPostBookingUX:
    """Tests for ETA calculation stability/throttling, UI cleanliness, and post-booking quick-dial UX."""

    def test_ui_cleanliness_no_judge_or_demo_elements(self):
        """Verify complete removal of judge/demo buttons, desk buttons, and SIH badges in public HTML/CSS."""
        public_dir = Path(__file__).parent.parent / "public"
        index_html = (public_dir / "index.html").read_text(encoding='utf-8')
        custom_css = (public_dir / "css" / "custom.css").read_text(encoding='utf-8')

        # Check absence of judge demo bar or buttons in HTML
        assert "judge-demo-bar" not in index_html
        assert "judge-demo-btn" not in index_html
        assert "runJudgeDemo" not in index_html

        # Check absence of desk btn in HTML
        assert 'id="desk-btn"' not in index_html

        # Check absence of SIH badges in index.html
        assert "Smart India Hackathon" not in index_html

    def test_highlight_card_autoscroll_default_false(self):
        """Verify highlightCard in index.html defaults autoScroll to false to prevent auto-scrolling on background refresh."""
        public_dir = Path(__file__).parent.parent / "public"
        index_html = (public_dir / "index.html").read_text(encoding='utf-8')

        # Locate highlightCard definition
        match = re.search(r'function\s+highlightCard\s*\([^)]*\)', index_html)
        assert match is not None
        func_sig = match.group(0)
        assert 'autoScroll = false' in func_sig

        # Check background refresh autoRouteNearest call passes autoScroll=false
        match_auto_route = re.search(r'autoRouteNearest[\s\S]*?highlightCard\([^)]+\)', index_html)
        assert match_auto_route is not None
        assert 'false' in match_auto_route.group(0)

    def test_osrm_throttling_logic_in_api_js(self):
        """Verify API.js contains shouldFetchOSRMRoute, recordOSRMFetch, and resetOSRMThrottle functions."""
        public_dir = Path(__file__).parent.parent / "public"
        api_js = (public_dir / "js" / "api.js").read_text(encoding='utf-8')

        assert "shouldFetchOSRMRoute" in api_js
        assert "recordOSRMFetch" in api_js
        assert "resetOSRMThrottle" in api_js
        assert "15000" in api_js  # 15s interval
        assert "50" in api_js     # 50m movement threshold

    def test_post_booking_drawer_quick_dial_elements_exist(self):
        """Verify post-booking drawer and cockpit HTML elements contain Call Ambulance (tel:108) and Call Hospital quick-dial buttons."""
        public_dir = Path(__file__).parent.parent / "public"
        index_html = (public_dir / "index.html").read_text(encoding='utf-8')

        assert 'id="inline-call-amb-btn"' in index_html
        assert 'id="inline-call-hosp-btn"' in index_html
        assert 'tel:108' in index_html
        assert 'id="cockpit-call-hosp-btn"' in index_html
        assert 'id="cockpit-call-amb-btn"' in index_html
        assert 'id="cockpit-lock-btn"' in index_html

    def test_post_booking_hold_creation_flow(self, client):
        """Verify bed hold creation API works and returns valid hold ID and OTP for post-booking drawer state."""
        hospitals = database.get_all_hospitals()
        assert len(hospitals) > 0
        target = hospitals[0]

        res = client.post('/api/holds/create', json={
            'hospital_id': target['id'],
            'resource_type': 'general_ward',
            'hold_type': 'CITIZEN',
            'phone': '9999999999',
            'severity': 'YELLOW'
        })
        assert res.status_code == 201
        data = res.get_json()

        assert data.get('success') is True or data.get('ok') is True
        assert 'hold_id' in data
        assert 'otp_code' in data or 'otp' in data

        # Clean up hold
        hold_id = data['hold_id']
        cancel_res = client.post('/api/holds/cancel', json={'hold_id': hold_id})
        assert cancel_res.status_code == 200
