# ============================================================
# PulseGrid - Database Module
# Member 2's Domain
#
# This file handles ALL database operations using Supabase.
# It connects to a PostgreSQL database hosted on Supabase
# and provides simple functions for each operation.
# ============================================================

import os
import random
from datetime import datetime, timezone, timedelta

try:
    from supabase import create_client
except ImportError:
    create_client = None

# The Supabase client - initialized once when the server starts
supabase = None

# In-memory mock database store used when SUPABASE_URL / KEY are not configured
MOCK_HOSPITALS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "SSKM Hospital (IPGMER)",
        "address": "244 AJC Bose Road, Bhowanipore, Kolkata 700020",
        "latitude": 22.5392, "longitude": 88.3433,
        "phone": "+91-33-2223-1589", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 38, "nurses_on_duty": 72,
        "adult_icu_total": 60, "adult_icu_occupied": 51, "adult_icu_held": 2,
        "pediatric_icu_total": 20, "pediatric_icu_occupied": 16, "pediatric_icu_held": 1,
        "cardiac_icu_total": 25, "cardiac_icu_occupied": 20, "cardiac_icu_held": 1,
        "general_ward_total": 400, "general_ward_occupied": 340, "general_ward_held": 8,
        "specialties": ["cardiac", "trauma", "pediatric", "neurosurgery", "burns", "nephrology"],
        "blood_stock_summary": {"A+": 18, "B+": 24, "O+": 35, "O-": 6, "AB+": 10, "A-": 4, "B-": 7, "AB-": 3}
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "Calcutta Medical College & Hospital",
        "address": "88 College Street, College Square, Kolkata 700073",
        "latitude": 22.5744, "longitude": 88.3629,
        "phone": "+91-33-2241-4900", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 34, "nurses_on_duty": 65,
        "adult_icu_total": 50, "adult_icu_occupied": 42, "adult_icu_held": 2,
        "pediatric_icu_total": 25, "pediatric_icu_occupied": 18, "pediatric_icu_held": 1,
        "cardiac_icu_total": 20, "cardiac_icu_occupied": 16, "cardiac_icu_held": 1,
        "general_ward_total": 350, "general_ward_occupied": 290, "general_ward_held": 6,
        "specialties": ["cardiac", "trauma", "pediatric", "maternity", "nephrology", "oncology"],
        "blood_stock_summary": {"A+": 20, "B+": 28, "O+": 40, "O-": 8, "AB+": 12, "A-": 5, "B-": 8, "AB-": 4}
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "name": "RG Kar Medical College & Hospital",
        "address": "1 Khudiram Bose Sarani, Belgachia, Kolkata 700004",
        "latitude": 22.6042, "longitude": 88.3734,
        "phone": "+91-33-2555-7675", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 28, "nurses_on_duty": 54,
        "adult_icu_total": 40, "adult_icu_occupied": 34, "adult_icu_held": 2,
        "pediatric_icu_total": 15, "pediatric_icu_occupied": 11, "pediatric_icu_held": 1,
        "cardiac_icu_total": 15, "cardiac_icu_occupied": 12, "cardiac_icu_held": 0,
        "general_ward_total": 280, "general_ward_occupied": 235, "general_ward_held": 5,
        "specialties": ["trauma", "cardiac", "pediatric", "orthopedics", "general", "maternity"],
        "blood_stock_summary": {"A+": 12, "B+": 18, "O+": 25, "O-": 4, "AB+": 7, "A-": 3, "B-": 5, "AB-": 2}
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "name": "NRS Medical College & Hospital",
        "address": "138 AJC Bose Road, Sealdah, Kolkata 700014",
        "latitude": 22.5645, "longitude": 88.3697,
        "phone": "+91-33-2286-0033", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 26, "nurses_on_duty": 50,
        "adult_icu_total": 40, "adult_icu_occupied": 34, "adult_icu_held": 2,
        "pediatric_icu_total": 14, "pediatric_icu_occupied": 10, "pediatric_icu_held": 1,
        "cardiac_icu_total": 18, "cardiac_icu_occupied": 14, "cardiac_icu_held": 1,
        "general_ward_total": 300, "general_ward_occupied": 252, "general_ward_held": 5,
        "specialties": ["cardiac", "trauma", "neurology", "maternity", "general"],
        "blood_stock_summary": {"A+": 14, "B+": 20, "O+": 28, "O-": 5, "AB+": 8, "A-": 3, "B-": 6, "AB-": 2}
    },
    {
        "id": "55555555-5555-5555-5555-555555555555",
        "name": "Beliaghata General Hospital",
        "address": "141 Beliaghata Main Road, Kolkata 700010",
        "latitude": 22.5754, "longitude": 88.3902,
        "phone": "+91-33-2360-1261", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 16, "nurses_on_duty": 32,
        "adult_icu_total": 25, "adult_icu_occupied": 21, "adult_icu_held": 1,
        "pediatric_icu_total": 10, "pediatric_icu_occupied": 8, "pediatric_icu_held": 0,
        "cardiac_icu_total": 8, "cardiac_icu_occupied": 6, "cardiac_icu_held": 0,
        "general_ward_total": 200, "general_ward_occupied": 168, "general_ward_held": 4,
        "specialties": ["general", "trauma", "maternity", "pediatric"],
        "blood_stock_summary": {"A+": 8, "B+": 12, "O+": 16, "O-": 2, "AB+": 4, "A-": 2, "B-": 3, "AB-": 1}
    },
    {
        "id": "66666666-6666-6666-6666-666666666666",
        "name": "Bangur Institute of Neurosciences",
        "address": "4 Deen Dayal Upadhyay Sarani, Kolkata 700025",
        "latitude": 22.5389, "longitude": 88.3380,
        "phone": "+91-33-2454-1984", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 18, "nurses_on_duty": 36,
        "adult_icu_total": 30, "adult_icu_occupied": 25, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 6, "pediatric_icu_held": 0,
        "cardiac_icu_total": 6, "cardiac_icu_occupied": 5, "cardiac_icu_held": 0,
        "general_ward_total": 150, "general_ward_occupied": 126, "general_ward_held": 3,
        "specialties": ["neurology", "neurosurgery", "trauma", "general"],
        "blood_stock_summary": {"A+": 6, "B+": 10, "O+": 14, "O-": 2, "AB+": 4, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "77777777-7777-7777-7777-777777777777",
        "name": "Chittaranjan National Cancer Institute",
        "address": "37 SP Mukherjee Road, Kolkata 700026",
        "latitude": 22.5286, "longitude": 88.3481,
        "phone": "+91-33-2476-5101", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 22, "nurses_on_duty": 44,
        "adult_icu_total": 20, "adult_icu_occupied": 17, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 6, "pediatric_icu_held": 0,
        "cardiac_icu_total": 6, "cardiac_icu_occupied": 5, "cardiac_icu_held": 0,
        "general_ward_total": 180, "general_ward_occupied": 152, "general_ward_held": 3,
        "specialties": ["oncology", "general", "maternity"],
        "blood_stock_summary": {"A+": 10, "B+": 14, "O+": 20, "O-": 3, "AB+": 6, "A-": 2, "B-": 4, "AB-": 1}
    },
    {
        "id": "88888888-8888-8888-8888-888888888888",
        "name": "Calcutta National Medical College & Hospital",
        "address": "32 Gorachand Road, Beniapukur, Kolkata 700014",
        "latitude": 22.5523, "longitude": 88.3705,
        "phone": "+91-33-2265-5325", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 20, "nurses_on_duty": 40,
        "adult_icu_total": 28, "adult_icu_occupied": 23, "adult_icu_held": 1,
        "pediatric_icu_total": 10, "pediatric_icu_occupied": 8, "pediatric_icu_held": 0,
        "cardiac_icu_total": 10, "cardiac_icu_occupied": 8, "cardiac_icu_held": 0,
        "general_ward_total": 220, "general_ward_occupied": 185, "general_ward_held": 4,
        "specialties": ["general", "trauma", "maternity", "pediatric", "orthopedics"],
        "blood_stock_summary": {"A+": 8, "B+": 12, "O+": 17, "O-": 2, "AB+": 5, "A-": 2, "B-": 3, "AB-": 1}
    },
    {
        "id": "99999999-9999-9999-9999-999999999999",
        "name": "ESI Hospital Sealdah",
        "address": "108 Dr. S. N. Chatterjee Road, Sealdah, Kolkata 700014",
        "latitude": 22.5680, "longitude": 88.3696,
        "phone": "+91-33-2350-1661", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 12, "nurses_on_duty": 24,
        "adult_icu_total": 18, "adult_icu_occupied": 14, "adult_icu_held": 1,
        "pediatric_icu_total": 6, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 6, "cardiac_icu_occupied": 5, "cardiac_icu_held": 0,
        "general_ward_total": 150, "general_ward_occupied": 120, "general_ward_held": 3,
        "specialties": ["general", "trauma", "maternity"],
        "blood_stock_summary": {"A+": 6, "B+": 8, "O+": 12, "O-": 2, "AB+": 3, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "Apollo Multispecialty Hospital",
        "address": "58 Canal Circular Road, Kankurgachi, Kolkata 700054",
        "latitude": 22.5786, "longitude": 88.3981,
        "phone": "+91-33-2320-3040", "emergency_phone": "1066",
        "type": "Private",
        "doctors_on_duty": 40, "nurses_on_duty": 75,
        "adult_icu_total": 60, "adult_icu_occupied": 45, "adult_icu_held": 3,
        "pediatric_icu_total": 25, "pediatric_icu_occupied": 16, "pediatric_icu_held": 2,
        "cardiac_icu_total": 30, "cardiac_icu_occupied": 22, "cardiac_icu_held": 2,
        "general_ward_total": 300, "general_ward_occupied": 220, "general_ward_held": 6,
        "specialties": ["cardiac", "trauma", "pediatric", "oncology", "transplant", "neurosurgery", "urology"],
        "blood_stock_summary": {"A+": 25, "B+": 35, "O+": 50, "O-": 10, "AB+": 18, "A-": 7, "B-": 10, "AB-": 5}
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "name": "Fortis Hospital Anandapur",
        "address": "730 Anandapur, EM Bypass, Kolkata 700107",
        "latitude": 22.5168, "longitude": 88.4005,
        "phone": "+91-33-6628-4444", "emergency_phone": "10501",
        "type": "Private",
        "doctors_on_duty": 32, "nurses_on_duty": 60,
        "adult_icu_total": 45, "adult_icu_occupied": 33, "adult_icu_held": 2,
        "pediatric_icu_total": 18, "pediatric_icu_occupied": 12, "pediatric_icu_held": 1,
        "cardiac_icu_total": 25, "cardiac_icu_occupied": 18, "cardiac_icu_held": 1,
        "general_ward_total": 220, "general_ward_occupied": 162, "general_ward_held": 4,
        "specialties": ["cardiac", "urology", "orthopedics", "pulmonology", "trauma", "neurology"],
        "blood_stock_summary": {"A+": 18, "B+": 25, "O+": 35, "O-": 7, "AB+": 12, "A-": 5, "B-": 7, "AB-": 3}
    },
    {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "name": "Medica Superspecialty Hospital",
        "address": "127 Mukundapur, EM Bypass, Kolkata 700099",
        "latitude": 22.5340, "longitude": 88.4116,
        "phone": "+91-33-4012-8888", "emergency_phone": "1800-103-5555",
        "type": "Private",
        "doctors_on_duty": 35, "nurses_on_duty": 65,
        "adult_icu_total": 50, "adult_icu_occupied": 37, "adult_icu_held": 2,
        "pediatric_icu_total": 18, "pediatric_icu_occupied": 12, "pediatric_icu_held": 1,
        "cardiac_icu_total": 22, "cardiac_icu_occupied": 16, "cardiac_icu_held": 1,
        "general_ward_total": 250, "general_ward_occupied": 185, "general_ward_held": 5,
        "specialties": ["cardiac", "trauma", "orthopedics", "neurology", "oncology", "transplant"],
        "blood_stock_summary": {"A+": 20, "B+": 28, "O+": 40, "O-": 8, "AB+": 14, "A-": 5, "B-": 8, "AB-": 3}
    },
    {
        "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        "name": "AMRI Hospital Dhakuria",
        "address": "JC 16/17, Salt Lake City Sector III, Kolkata 700098",
        "latitude": 22.5023, "longitude": 88.3599,
        "phone": "+91-33-6680-0000", "emergency_phone": "1800-103-2800",
        "type": "Private",
        "doctors_on_duty": 28, "nurses_on_duty": 55,
        "adult_icu_total": 40, "adult_icu_occupied": 29, "adult_icu_held": 2,
        "pediatric_icu_total": 14, "pediatric_icu_occupied": 9, "pediatric_icu_held": 1,
        "cardiac_icu_total": 18, "cardiac_icu_occupied": 13, "cardiac_icu_held": 1,
        "general_ward_total": 200, "general_ward_occupied": 148, "general_ward_held": 4,
        "specialties": ["cardiac", "orthopedics", "urology", "gastroenterology", "neurology"],
        "blood_stock_summary": {"A+": 14, "B+": 20, "O+": 28, "O-": 5, "AB+": 10, "A-": 4, "B-": 6, "AB-": 2}
    },
    {
        "id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
        "name": "AMRI Hospital Salt Lake",
        "address": "Block-B, Plot 1, Action Area II, Newtown, Kolkata 700136",
        "latitude": 22.5742, "longitude": 88.4161,
        "phone": "+91-33-6680-1000", "emergency_phone": "1800-103-2800",
        "type": "Private",
        "doctors_on_duty": 24, "nurses_on_duty": 46,
        "adult_icu_total": 35, "adult_icu_occupied": 25, "adult_icu_held": 2,
        "pediatric_icu_total": 12, "pediatric_icu_occupied": 8, "pediatric_icu_held": 1,
        "cardiac_icu_total": 15, "cardiac_icu_occupied": 11, "cardiac_icu_held": 0,
        "general_ward_total": 180, "general_ward_occupied": 132, "general_ward_held": 3,
        "specialties": ["cardiac", "orthopedics", "neurology", "gastroenterology"],
        "blood_stock_summary": {"A+": 12, "B+": 16, "O+": 22, "O-": 4, "AB+": 8, "A-": 3, "B-": 5, "AB-": 2}
    },
    {
        "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
        "name": "Belle Vue Clinic",
        "address": "9 Dr. U. N. Brahmachari Street, Kolkata 700017",
        "latitude": 22.5533, "longitude": 88.3535,
        "phone": "+91-33-2287-2321", "emergency_phone": "+91-33-2287-2321",
        "type": "Private",
        "doctors_on_duty": 20, "nurses_on_duty": 38,
        "adult_icu_total": 25, "adult_icu_occupied": 18, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 5, "pediatric_icu_held": 0,
        "cardiac_icu_total": 12, "cardiac_icu_occupied": 9, "cardiac_icu_held": 0,
        "general_ward_total": 120, "general_ward_occupied": 88, "general_ward_held": 2,
        "specialties": ["cardiac", "general", "maternity", "orthopedics"],
        "blood_stock_summary": {"A+": 8, "B+": 12, "O+": 16, "O-": 3, "AB+": 5, "A-": 2, "B-": 3, "AB-": 1}
    },
    {
        "id": "11111111-2222-3333-4444-555555555555",
        "name": "Woodlands Multispecialty Hospital",
        "address": "8/5 Alipore Road, Alipore, Kolkata 700027",
        "latitude": 22.5341, "longitude": 88.3395,
        "phone": "+91-33-4012-3456", "emergency_phone": "+91-33-4012-3456",
        "type": "Private",
        "doctors_on_duty": 22, "nurses_on_duty": 42,
        "adult_icu_total": 28, "adult_icu_occupied": 20, "adult_icu_held": 1,
        "pediatric_icu_total": 10, "pediatric_icu_occupied": 7, "pediatric_icu_held": 0,
        "cardiac_icu_total": 14, "cardiac_icu_occupied": 10, "cardiac_icu_held": 1,
        "general_ward_total": 140, "general_ward_occupied": 104, "general_ward_held": 2,
        "specialties": ["cardiac", "orthopedics", "neurology", "general", "maternity"],
        "blood_stock_summary": {"A+": 10, "B+": 14, "O+": 18, "O-": 3, "AB+": 6, "A-": 2, "B-": 4, "AB-": 1}
    },
    {
        "id": "22222222-3333-4444-5555-666666666666",
        "name": "Ruby General Hospital",
        "address": "576 Anandapur, EM Bypass, Kolkata 700107",
        "latitude": 22.5193, "longitude": 88.3977,
        "phone": "+91-33-6600-0822", "emergency_phone": "+91-33-6600-0822",
        "type": "Private",
        "doctors_on_duty": 20, "nurses_on_duty": 38,
        "adult_icu_total": 28, "adult_icu_occupied": 20, "adult_icu_held": 1,
        "pediatric_icu_total": 10, "pediatric_icu_occupied": 7, "pediatric_icu_held": 0,
        "cardiac_icu_total": 12, "cardiac_icu_occupied": 9, "cardiac_icu_held": 0,
        "general_ward_total": 150, "general_ward_occupied": 110, "general_ward_held": 3,
        "specialties": ["cardiac", "orthopedics", "general", "urology"],
        "blood_stock_summary": {"A+": 9, "B+": 13, "O+": 18, "O-": 3, "AB+": 6, "A-": 2, "B-": 3, "AB-": 1}
    },
    {
        "id": "33333333-4444-5555-6666-777777777777",
        "name": "Nightingale Hospital",
        "address": "11 Shakespeare Sarani, Kolkata 700071",
        "latitude": 22.5580, "longitude": 88.3550,
        "phone": "+91-33-2282-5552", "emergency_phone": "+91-33-2282-5552",
        "type": "Private",
        "doctors_on_duty": 14, "nurses_on_duty": 28,
        "adult_icu_total": 20, "adult_icu_occupied": 14, "adult_icu_held": 1,
        "pediatric_icu_total": 6, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 8, "cardiac_icu_occupied": 6, "cardiac_icu_held": 0,
        "general_ward_total": 100, "general_ward_occupied": 74, "general_ward_held": 2,
        "specialties": ["general", "maternity", "orthopedics"],
        "blood_stock_summary": {"A+": 6, "B+": 8, "O+": 12, "O-": 2, "AB+": 4, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "44444444-5555-6666-7777-888888888888",
        "name": "BM Birla Heart Research Centre",
        "address": "1/1 National Library Avenue, Kolkata 700027",
        "latitude": 22.5290, "longitude": 88.3487,
        "phone": "+91-33-6626-3030", "emergency_phone": "+91-33-6626-3030",
        "type": "Private",
        "doctors_on_duty": 18, "nurses_on_duty": 35,
        "adult_icu_total": 20, "adult_icu_occupied": 14, "adult_icu_held": 1,
        "pediatric_icu_total": 6, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 30, "cardiac_icu_occupied": 22, "cardiac_icu_held": 2,
        "general_ward_total": 100, "general_ward_occupied": 72, "general_ward_held": 2,
        "specialties": ["cardiac", "cardiothoracic"],
        "blood_stock_summary": {"A+": 10, "B+": 14, "O+": 20, "O-": 4, "AB+": 7, "A-": 3, "B-": 4, "AB-": 2}
    },
    {
        "id": "55555555-6666-7777-8888-999999999999",
        "name": "Narayana Multispecialty Hospital Howrah",
        "address": "78 Jessore Road South, Noapara, Kolkata 700125",
        "latitude": 22.6220, "longitude": 88.3870,
        "phone": "+91-33-7122-2000", "emergency_phone": "1800-425-8500",
        "type": "Private",
        "doctors_on_duty": 28, "nurses_on_duty": 52,
        "adult_icu_total": 40, "adult_icu_occupied": 29, "adult_icu_held": 2,
        "pediatric_icu_total": 15, "pediatric_icu_occupied": 10, "pediatric_icu_held": 1,
        "cardiac_icu_total": 20, "cardiac_icu_occupied": 14, "cardiac_icu_held": 1,
        "general_ward_total": 200, "general_ward_occupied": 148, "general_ward_held": 4,
        "specialties": ["cardiac", "trauma", "pediatric", "orthopedics", "neurology"],
        "blood_stock_summary": {"A+": 14, "B+": 20, "O+": 28, "O-": 5, "AB+": 10, "A-": 4, "B-": 6, "AB-": 2}
    },
    {
        "id": "66666666-7777-8888-9999-aaaaaaaaaaaa",
        "name": "ILS Hospitals Salt Lake",
        "address": "P4 CIT Scheme LXXII, Block A, Ultadanga, Kolkata 700054",
        "latitude": 22.5787, "longitude": 88.4170,
        "phone": "+91-33-4012-9999", "emergency_phone": "+91-33-4012-9999",
        "type": "Private",
        "doctors_on_duty": 18, "nurses_on_duty": 34,
        "adult_icu_total": 25, "adult_icu_occupied": 18, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 5, "pediatric_icu_held": 0,
        "cardiac_icu_total": 10, "cardiac_icu_occupied": 7, "cardiac_icu_held": 0,
        "general_ward_total": 130, "general_ward_occupied": 96, "general_ward_held": 2,
        "specialties": ["general", "orthopedics", "cardiac", "maternity"],
        "blood_stock_summary": {"A+": 8, "B+": 11, "O+": 15, "O-": 2, "AB+": 5, "A-": 2, "B-": 3, "AB-": 1}
    },
    {
        "id": "77777777-8888-9999-aaaa-bbbbbbbbbbbb",
        "name": "Desun Hospital",
        "address": "Monirampur, Kasba Industrial Estate, Kolkata 700107",
        "latitude": 22.5022, "longitude": 88.4008,
        "phone": "+91-33-4065-9999", "emergency_phone": "+91-33-4065-9999",
        "type": "Private",
        "doctors_on_duty": 16, "nurses_on_duty": 30,
        "adult_icu_total": 22, "adult_icu_occupied": 16, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 5, "pediatric_icu_held": 0,
        "cardiac_icu_total": 10, "cardiac_icu_occupied": 7, "cardiac_icu_held": 0,
        "general_ward_total": 120, "general_ward_occupied": 88, "general_ward_held": 2,
        "specialties": ["general", "orthopedics", "urology", "cardiac"],
        "blood_stock_summary": {"A+": 7, "B+": 10, "O+": 14, "O-": 2, "AB+": 4, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "88888888-9999-aaaa-bbbb-cccccccccccc",
        "name": "Charnock Hospital",
        "address": "Premises No. 45, Rajdanga Main Road, Kasba, Kolkata 700107",
        "latitude": 22.4966, "longitude": 88.4063,
        "phone": "+91-33-4044-4444", "emergency_phone": "+91-33-4044-4444",
        "type": "Private",
        "doctors_on_duty": 14, "nurses_on_duty": 28,
        "adult_icu_total": 18, "adult_icu_occupied": 13, "adult_icu_held": 1,
        "pediatric_icu_total": 6, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 8, "cardiac_icu_occupied": 6, "cardiac_icu_held": 0,
        "general_ward_total": 100, "general_ward_occupied": 74, "general_ward_held": 2,
        "specialties": ["general", "orthopedics", "cardiac", "maternity"],
        "blood_stock_summary": {"A+": 6, "B+": 9, "O+": 12, "O-": 2, "AB+": 4, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "99999999-aaaa-bbbb-cccc-dddddddddddd",
        "name": "CMRI Hospital",
        "address": "7/2 Diamond Harbour Road, Kolkata 700027",
        "latitude": 22.5444, "longitude": 88.3338,
        "phone": "+91-33-2455-8600", "emergency_phone": "+91-33-2455-8600",
        "type": "Private",
        "doctors_on_duty": 20, "nurses_on_duty": 38,
        "adult_icu_total": 25, "adult_icu_occupied": 18, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 5, "pediatric_icu_held": 0,
        "cardiac_icu_total": 12, "cardiac_icu_occupied": 9, "cardiac_icu_held": 0,
        "general_ward_total": 130, "general_ward_occupied": 96, "general_ward_held": 2,
        "specialties": ["cardiac", "orthopedics", "general", "gastroenterology"],
        "blood_stock_summary": {"A+": 8, "B+": 11, "O+": 15, "O-": 2, "AB+": 5, "A-": 2, "B-": 3, "AB-": 1}
    },
    {
        "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "name": "Park Clinic",
        "address": "4 Gorky Terrace, Elgin, Kolkata 700017",
        "latitude": 22.5441, "longitude": 88.3586,
        "phone": "+91-33-2454-5454", "emergency_phone": "+91-33-2454-5454",
        "type": "Private",
        "doctors_on_duty": 16, "nurses_on_duty": 30,
        "adult_icu_total": 20, "adult_icu_occupied": 14, "adult_icu_held": 1,
        "pediatric_icu_total": 6, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 10, "cardiac_icu_occupied": 7, "cardiac_icu_held": 0,
        "general_ward_total": 100, "general_ward_occupied": 73, "general_ward_held": 2,
        "specialties": ["general", "cardiac", "maternity", "orthopedics"],
        "blood_stock_summary": {"A+": 7, "B+": 10, "O+": 14, "O-": 2, "AB+": 4, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "bbbbbbbb-cccc-dddd-eeee-ffffffffffff",
        "name": "Peerless Hospital",
        "address": "360 Panchasayar, Kolkata 700094",
        "latitude": 22.4803, "longitude": 88.3976,
        "phone": "+91-33-4011-1222", "emergency_phone": "+91-33-4011-1222",
        "type": "Private",
        "doctors_on_duty": 26, "nurses_on_duty": 50,
        "adult_icu_total": 35, "adult_icu_occupied": 25, "adult_icu_held": 2,
        "pediatric_icu_total": 12, "pediatric_icu_occupied": 8, "pediatric_icu_held": 1,
        "cardiac_icu_total": 15, "cardiac_icu_occupied": 11, "cardiac_icu_held": 1,
        "general_ward_total": 180, "general_ward_occupied": 132, "general_ward_held": 3,
        "specialties": ["cardiac", "orthopedics", "neurology", "gastroenterology", "urology"],
        "blood_stock_summary": {"A+": 12, "B+": 17, "O+": 24, "O-": 4, "AB+": 8, "A-": 3, "B-": 5, "AB-": 2}
    },
    {
        "id": "cccccccc-dddd-eeee-ffff-111111111111",
        "name": "Kothari Medical Centre",
        "address": "8/3 Alipore Road, Alipore, Kolkata 700027",
        "latitude": 22.5445, "longitude": 88.3389,
        "phone": "+91-33-2459-0870", "emergency_phone": "+91-33-2459-0870",
        "type": "Private",
        "doctors_on_duty": 12, "nurses_on_duty": 24,
        "adult_icu_total": 16, "adult_icu_occupied": 11, "adult_icu_held": 1,
        "pediatric_icu_total": 5, "pediatric_icu_occupied": 3, "pediatric_icu_held": 0,
        "cardiac_icu_total": 8, "cardiac_icu_occupied": 6, "cardiac_icu_held": 0,
        "general_ward_total": 80, "general_ward_occupied": 58, "general_ward_held": 1,
        "specialties": ["general", "orthopedics", "maternity"],
        "blood_stock_summary": {"A+": 5, "B+": 7, "O+": 10, "O-": 1, "AB+": 3, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "dddddddd-eeee-ffff-1111-222222222222",
        "name": "Shambhunath Pandit Hospital",
        "address": "6 Suren Sarkar Road, Beniapukur, Kolkata 700014",
        "latitude": 22.5519, "longitude": 88.3697,
        "phone": "+91-33-2265-5301", "emergency_phone": "102",
        "type": "Government",
        "doctors_on_duty": 10, "nurses_on_duty": 20,
        "adult_icu_total": 14, "adult_icu_occupied": 11, "adult_icu_held": 0,
        "pediatric_icu_total": 5, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 4, "cardiac_icu_occupied": 3, "cardiac_icu_held": 0,
        "general_ward_total": 120, "general_ward_occupied": 100, "general_ward_held": 2,
        "specialties": ["maternity", "general", "pediatric"],
        "blood_stock_summary": {"A+": 4, "B+": 6, "O+": 9, "O-": 1, "AB+": 2, "A-": 1, "B-": 1, "AB-": 0}
    },
    {
        "id": "eeeeeeee-ffff-1111-2222-333333333333",
        "name": "Techno India DAMA Hospital",
        "address": "DL-32, Sector-II, Bidhannagar, Kolkata 700091",
        "latitude": 22.5699, "longitude": 88.4337,
        "phone": "+91-33-2357-3777", "emergency_phone": "+91-33-2357-3777",
        "type": "Private",
        "doctors_on_duty": 14, "nurses_on_duty": 26,
        "adult_icu_total": 18, "adult_icu_occupied": 13, "adult_icu_held": 1,
        "pediatric_icu_total": 6, "pediatric_icu_occupied": 4, "pediatric_icu_held": 0,
        "cardiac_icu_total": 8, "cardiac_icu_occupied": 6, "cardiac_icu_held": 0,
        "general_ward_total": 100, "general_ward_occupied": 73, "general_ward_held": 2,
        "specialties": ["general", "orthopedics", "cardiac", "maternity"],
        "blood_stock_summary": {"A+": 6, "B+": 9, "O+": 12, "O-": 2, "AB+": 4, "A-": 1, "B-": 2, "AB-": 1}
    },
    {
        "id": "ffffffff-1111-2222-3333-444444444444",
        "name": "Columbia Asia Hospital Kolkata",
        "address": "AA1, Major Arterial Road, New Town, Kolkata 700156",
        "latitude": 22.6035, "longitude": 88.4295,
        "phone": "+91-33-6628-3000", "emergency_phone": "+91-33-6628-3000",
        "type": "Private",
        "doctors_on_duty": 20, "nurses_on_duty": 38,
        "adult_icu_total": 24, "adult_icu_occupied": 17, "adult_icu_held": 1,
        "pediatric_icu_total": 8, "pediatric_icu_occupied": 5, "pediatric_icu_held": 0,
        "cardiac_icu_total": 10, "cardiac_icu_occupied": 7, "cardiac_icu_held": 0,
        "general_ward_total": 120, "general_ward_occupied": 88, "general_ward_held": 2,
        "specialties": ["general", "cardiac", "orthopedics", "pediatric"],
        "blood_stock_summary": {"A+": 8, "B+": 11, "O+": 15, "O-": 2, "AB+": 5, "A-": 2, "B-": 3, "AB-": 1}
    },
]
MOCK_HOLDS = []


def init_supabase():
    """
    Connects to our Supabase database using the URL and key
    from the .env file. Must be called once when the server starts.
    """
    global supabase
    try:
        if create_client is None:
            print("[DATABASE] NOTICE: supabase package not installed. Running in Offline Mock Mode with 6 Kolkata hospitals.")
            return None

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            print("[DATABASE] NOTICE: SUPABASE_URL / KEY not set in .env. Running in Offline Mock Mode with 6 Kolkata hospitals.")
            return None

        supabase = create_client(url, key)
        print("[DATABASE] Supabase client initialized successfully")
        return supabase
    except Exception as e:
        print(f"[DATABASE] Error initializing Supabase ({e}). Running in Offline Mock Mode.")
        return None


def _safe_int(value):
    """
    Safely converts a value to integer. Returns 0 if the value
    is None, empty string, or not a number. This prevents crashes
    when database columns have NULL values.
    """
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _format_hospital(h):
    """
    Takes a raw hospital row from Supabase and adds a 'wards'
    dictionary that the frontend JavaScript expects. Also calculates
    available beds for each ward type.
    
    Example output wards:
    {
        "Adult ICU": { "total": 14, "occupied": 10, "held": 1, "available": 3 },
        "Pediatric ICU": { "total": 6, "occupied": 4, "held": 0, "available": 2 },
        ...
    }
    """
    ward_types = [
        ("Adult ICU", "adult_icu"),
        ("Pediatric ICU", "pediatric_icu"),
        ("Cardiac ICU", "cardiac_icu"),
        ("General", "general_ward"),
    ]

    wards = {}
    for display_name, db_prefix in ward_types:
        total = _safe_int(h.get(f"{db_prefix}_total"))
        occupied = _safe_int(h.get(f"{db_prefix}_occupied"))
        held = _safe_int(h.get(f"{db_prefix}_held"))
        available = max(0, total - occupied - held)

        wards[display_name] = {
            "total": total,
            "occupied": occupied,
            "held": held,
            "available": available,
            "db_key": db_prefix  # Used by frontend to create holds
        }

    h["wards"] = wards
    return h


def get_all_hospitals(specialty_filter=None, ward_filter=None):
    """
    Gets all hospitals from the database.
    
    - If specialty_filter is provided (like 'cardiac'), only returns
      hospitals that have that specialty.
    - If ward_filter is provided (like 'adult_icu'), only returns
      hospitals that have available beds in that specific ward.
    
    Returns a list of hospital dictionaries with a 'wards' field
    containing bed availability info for the frontend.
    """
    if not supabase:
        results = []
        for h in MOCK_HOSPITALS:
            if specialty_filter and specialty_filter not in h.get("specialties", []):
                continue
            if ward_filter:
                total = _safe_int(h.get(f"{ward_filter}_total"))
                occupied = _safe_int(h.get(f"{ward_filter}_occupied"))
                held = _safe_int(h.get(f"{ward_filter}_held"))
                available = total - occupied - held
                if available <= 0:
                    continue
            results.append(_format_hospital(dict(h)))
        return results

    try:
        query = supabase.table("hospitals").select("*")

        # Filter by specialty if requested
        if specialty_filter:
            query = query.contains("specialties", [specialty_filter])

        response = query.execute()
        hospitals = response.data

        # Format each hospital and optionally filter by ward availability
        results = []
        for h in hospitals:
            h = _format_hospital(h)

            if ward_filter:
                # Check if beds are available in the requested ward
                total = _safe_int(h.get(f"{ward_filter}_total"))
                occupied = _safe_int(h.get(f"{ward_filter}_occupied"))
                held = _safe_int(h.get(f"{ward_filter}_held"))
                available = total - occupied - held
                if available > 0:
                    results.append(h)
            else:
                results.append(h)

        return results
    except Exception as e:
        print(f"[DATABASE] Error getting hospitals: {e}")
        return []


def create_live_hold(hospital_id, resource_type, hold_type, requester_phone, severity):
    """
    Creates a temporary bed reservation (hold) at a hospital.
    """
    if not supabase:
        h = next((x for x in MOCK_HOSPITALS if x["id"] == hospital_id), None)
        if not h:
            return {"error": "Hospital not found"}

        total = _safe_int(h.get(f"{resource_type}_total"))
        occupied = _safe_int(h.get(f"{resource_type}_occupied"))
        held = _safe_int(h.get(f"{resource_type}_held"))
        available = total - occupied - held

        if available <= 0:
            return {"error": "No beds available in this ward"}

        otp_code = str(random.randint(1000, 9999))
        now_utc = datetime.now(timezone.utc)
        minutes = 15
        expires_at = now_utc + timedelta(minutes=minutes)

        hold_id = f"mock-hold-{random.randint(10000, 99999)}"
        hold_rec = {
            "id": hold_id,
            "hospital_id": hospital_id,
            "resource_type": resource_type,
            "hold_type": hold_type,
            "requester_phone": requester_phone,
            "otp_code": otp_code,
            "status": "ACTIVE",
            "severity": severity,
            "created_at": now_utc.isoformat(),
            "expires_at": expires_at.isoformat()
        }
        MOCK_HOLDS.append(hold_rec)
        h[f"{resource_type}_held"] = held + 1
        print(f"[DATABASE MOCK] Hold created: OTP={otp_code}, Hospital={hospital_id}, Ward={resource_type}")
        return {
            "otp_code": otp_code,
            "hold_id": hold_id,
            "expires_at": expires_at.isoformat(),
            "hold_type": hold_type,
            "status": "ACTIVE"
        }

    try:
        # Step 1: Get the hospital and check bed availability
        hospitals = supabase.table("hospitals").select("*").eq("id", hospital_id).execute().data
        if not hospitals:
            return {"error": "Hospital not found"}

        h = hospitals[0]
        total = _safe_int(h.get(f"{resource_type}_total"))
        occupied = _safe_int(h.get(f"{resource_type}_occupied"))
        held = _safe_int(h.get(f"{resource_type}_held"))
        available = total - occupied - held

        if available <= 0:
            return {"error": "No beds available in this ward"}

        # Step 2: Generate a random 4-digit OTP
        otp_code = str(random.randint(1000, 9999))

        # Step 3: Calculate expiry time
        now_utc = datetime.now(timezone.utc)
        minutes = 15
        expires_at = now_utc + timedelta(minutes=minutes)

        # Step 4: Insert the hold record
        hold_data = {
            "hospital_id": hospital_id,
            "resource_type": resource_type,
            "hold_type": hold_type,
            "requester_phone": requester_phone,
            "otp_code": otp_code,
            "status": "ACTIVE",
            "severity": severity,
            "created_at": now_utc.isoformat(),
            "expires_at": expires_at.isoformat()
        }
        hold_res = supabase.table("holds").insert(hold_data).execute()

        # Step 5: Increment the hospital's held bed count
        supabase.table("hospitals").update({
            f"{resource_type}_held": held + 1
        }).eq("id", hospital_id).execute()

        print(f"[DATABASE] Hold created: OTP={otp_code}, Hospital={hospital_id}, Ward={resource_type}, Expires={expires_at}")

        # Return the OTP and hold info to the patient
        return {
            "otp": otp_code,
            "hold_id": hold_res.data[0]["id"],
            "expires_at": expires_at.isoformat(),
            "hold_type": hold_type,
            "minutes": minutes
        }
    except Exception as e:
        print(f"[DATABASE] Error creating hold: {e}")
        return {"error": str(e)}


def redeem_hold(hospital_id, otp_code):
    """
    Called when a nurse enters the 4-digit OTP at the hospital desk.
    """
    if not supabase:
        hold = next((x for x in MOCK_HOLDS if x["hospital_id"] == hospital_id and x["otp_code"] == str(otp_code) and x["status"] == "ACTIVE"), None)
        if not hold:
            return {"error": "Invalid OTP or no active hold found"}
        hold["status"] = "REDEEMED"
        hold["redeemed_at"] = datetime.now(timezone.utc).isoformat()
        h = next((x for x in MOCK_HOSPITALS if x["id"] == hospital_id), None)
        if h:
            res_type = hold["resource_type"]
            h[f"{res_type}_held"] = max(0, _safe_int(h.get(f"{res_type}_held")) - 1)
            h[f"{res_type}_occupied"] = _safe_int(h.get(f"{res_type}_occupied")) + 1
        print(f"[DATABASE MOCK] Hold redeemed: OTP={otp_code}, Hospital={hospital_id}")
        return {"success": True, "message": "Patient admitted successfully"}

    try:
        # Step 1: Find the matching active hold
        holds = supabase.table("holds").select("*") \
            .eq("hospital_id", hospital_id) \
            .eq("otp_code", otp_code) \
            .eq("status", "ACTIVE") \
            .execute().data

        if not holds:
            return {"error": "Invalid OTP or no active hold found"}

        hold = holds[0]
        hold_id = hold["id"]
        resource_type = hold["resource_type"]

        # Step 2: Mark the hold as REDEEMED
        now_utc = datetime.now(timezone.utc).isoformat()
        supabase.table("holds").update({
            "status": "REDEEMED",
            "redeemed_at": now_utc
        }).eq("id", hold_id).execute()

        # Step 3: Update hospital bed counts
        hospitals = supabase.table("hospitals").select("*").eq("id", hospital_id).execute().data
        if hospitals:
            h = hospitals[0]
            new_held = max(0, _safe_int(h.get(f"{resource_type}_held")) - 1)
            new_occupied = _safe_int(h.get(f"{resource_type}_occupied")) + 1
            supabase.table("hospitals").update({
                f"{resource_type}_held": new_held,
                f"{resource_type}_occupied": new_occupied
            }).eq("id", hospital_id).execute()

        print(f"[DATABASE] Hold redeemed: OTP={otp_code}, Hospital={hospital_id}")
        return {"success": True, "message": "Patient admitted successfully"}
    except Exception as e:
        print(f"[DATABASE] Error redeeming hold: {e}")
        return {"error": str(e)}


def release_expired_holds():
    """
    Called every 10 seconds by the TTL background worker.
    """
    if not supabase:
        now_utc = datetime.now(timezone.utc).isoformat()
        count = 0
        for hold in MOCK_HOLDS:
            if hold["status"] == "ACTIVE" and hold["expires_at"] < now_utc:
                hold["status"] = "EXPIRED"
                h = next((x for x in MOCK_HOSPITALS if x["id"] == hold["hospital_id"]), None)
                if h:
                    res_type = hold["resource_type"]
                    h[f"{res_type}_held"] = max(0, _safe_int(h.get(f"{res_type}_held")) - 1)
                count += 1
        return count

    try:
        now_utc = datetime.now(timezone.utc).isoformat()

        # Find all expired active holds
        holds = supabase.table("holds").select("*") \
            .eq("status", "ACTIVE") \
            .lt("expires_at", now_utc) \
            .execute().data

        count = 0
        for hold in holds:
            hold_id = hold["id"]
            hospital_id = hold["hospital_id"]
            resource_type = hold["resource_type"]

            # Mark as expired
            supabase.table("holds").update({
                "status": "EXPIRED"
            }).eq("id", hold_id).execute()

            # Free the held bed
            hospitals = supabase.table("hospitals").select("*").eq("id", hospital_id).execute().data
            if hospitals:
                h = hospitals[0]
                new_held = max(0, _safe_int(h.get(f"{resource_type}_held")) - 1)
                supabase.table("hospitals").update({
                    f"{resource_type}_held": new_held
                }).eq("id", hospital_id).execute()

            count += 1

        return count
    except Exception as e:
        print(f"[DATABASE] Error releasing expired holds: {e}")
        return 0


def update_quick_counter(hospital_id, ward, delta):
    """
    Called when a nurse taps [+] or [-] on the hospital tablet.
    """
    if not supabase:
        h = next((x for x in MOCK_HOSPITALS if x["id"] == hospital_id), None)
        if not h:
            return {"error": "Hospital not found"}
        total = _safe_int(h.get(f"{ward}_total"))
        occupied = _safe_int(h.get(f"{ward}_occupied"))
        new_occupied = max(0, min(total, occupied + delta))
        h[f"{ward}_occupied"] = new_occupied
        print(f"[DATABASE MOCK] Counter updated: Hospital={hospital_id}, Ward={ward}, {occupied} -> {new_occupied}")
        return {"success": True, "new_occupied": new_occupied, "total": total}

    try:
        hospitals = supabase.table("hospitals").select("*").eq("id", hospital_id).execute().data
        if not hospitals:
            return {"error": "Hospital not found"}

        h = hospitals[0]
        total = _safe_int(h.get(f"{ward}_total"))
        occupied = _safe_int(h.get(f"{ward}_occupied"))

        # Apply the change, but keep it within valid range
        new_occupied = occupied + delta
        if new_occupied < 0:
            new_occupied = 0
        if new_occupied > total:
            new_occupied = total

        supabase.table("hospitals").update({
            f"{ward}_occupied": new_occupied
        }).eq("id", hospital_id).execute()

        print(f"[DATABASE] Counter updated: Hospital={hospital_id}, Ward={ward}, {occupied} -> {new_occupied}")
        return {"success": True, "new_occupied": new_occupied, "total": total}
    except Exception as e:
        print(f"[DATABASE] Error updating counter: {e}")
        return {"error": str(e)}


def get_active_holds(hospital_id):
    """
    Gets all currently active holds for a specific hospital.
    Used by the hospital desk to show incoming patients.
    """
    if not supabase:
        return [dict(x) for x in MOCK_HOLDS if x["hospital_id"] == hospital_id and x["status"] == "ACTIVE"]

    try:
        response = supabase.table("holds").select("*") \
            .eq("hospital_id", hospital_id) \
            .eq("status", "ACTIVE") \
            .order("created_at", desc=False) \
            .execute()
        return response.data
    except Exception as e:
        print(f"[DATABASE] Error getting active holds: {e}")
        return []


def get_blood_inventory(hospital_id=None):
    """
    Gets blood inventory data, optionally filtered by hospital.
    Returns a list of blood records with group, component, and quantities.
    """
    if not supabase:
        inventory = []
        groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        components = ["PRBC", "Platelets", "Plasma"]
        target_hospitals = [h for h in MOCK_HOSPITALS if not hospital_id or h["id"] == hospital_id]
        for h in target_hospitals:
            for g in groups:
                for c in components:
                    units = h.get("blood_stock_summary", {}).get(g, 5)
                    inventory.append({
                        "id": f"mock-blood-{h['id'][:4]}-{g}-{c}",
                        "hospital_id": h["id"],
                        "hospital_name": h["name"],
                        "blood_group": g,
                        "component": c,
                        "units_available": units,
                        "status": "AVAILABLE" if units > 3 else ("CRITICAL" if units > 0 else "OUT_OF_STOCK")
                    })
        return inventory

    try:
        query = supabase.table("blood_inventory").select("*")
        if hospital_id:
            query = query.eq("hospital_id", hospital_id)

        response = query.execute()
        return response.data
    except Exception as e:
        print(f"[DATABASE] Error getting blood inventory: {e}")
        return []
