-- ============================================================
-- PULSEGRID DATABASE SCHEMA
-- Real-Time Emergency Hospital Bed & Blood Triage Engine
-- Smart India Hackathon (SIH) 2026
--
-- HOW TO USE:
-- 1. Go to supabase.com → Open your project
-- 2. Click "SQL Editor" in the left sidebar
-- 3. Click "+ New query"
-- 4. Paste this ENTIRE file
-- 5. Click the green "Run" button
-- 6. Go to "Table Editor" to verify tables were created
-- ============================================================

-- Enable UUID generation (usually already enabled on Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================
-- TABLE 1: HOSPITALS
-- One row per hospital. Tracks staffed beds per ward type.
-- "total" = staffed beds (not physical beds)
-- "occupied" = currently in use by a patient
-- "held" = reserved via PulseGrid TTL hold (patient en route)
-- Available = total - occupied - held
-- ============================================================
CREATE TABLE IF NOT EXISTS public.hospitals (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name            TEXT NOT NULL,
    address         TEXT,
    latitude        DOUBLE PRECISION DEFAULT 0,
    longitude       DOUBLE PRECISION DEFAULT 0,
    phone           TEXT,
    specialties     TEXT[] DEFAULT '{}',

    -- Adult ICU bed tracking
    adult_icu_total     INT DEFAULT 0,
    adult_icu_occupied  INT DEFAULT 0,
    adult_icu_held      INT DEFAULT 0,

    -- Pediatric ICU bed tracking
    pediatric_icu_total     INT DEFAULT 0,
    pediatric_icu_occupied  INT DEFAULT 0,
    pediatric_icu_held      INT DEFAULT 0,

    -- Cardiac ICU bed tracking
    cardiac_icu_total       INT DEFAULT 0,
    cardiac_icu_occupied    INT DEFAULT 0,
    cardiac_icu_held        INT DEFAULT 0,

    -- General / Oxygen ward bed tracking
    general_ward_total      INT DEFAULT 0,
    general_ward_occupied   INT DEFAULT 0,
    general_ward_held       INT DEFAULT 0,

    -- When this hospital's data was last updated
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE 2: HOLDS
-- Each row = one bed reservation.
-- Has a 4-digit OTP code and an expiry timestamp.
-- Lifecycle: ACTIVE → REDEEMED (patient arrived & checked in)
--         or ACTIVE → EXPIRED  (timer ran out / patient cancelled)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.holds (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    hospital_id     UUID REFERENCES public.hospitals(id) ON DELETE CASCADE NOT NULL,
    resource_type   TEXT NOT NULL,           -- 'adult_icu', 'pediatric_icu', 'cardiac_icu', 'general_ward'
    hold_type       TEXT DEFAULT 'citizen',  -- 'citizen' = 15 min TTL, 'paramedic' = 20 min TTL
    requester_phone TEXT,                    -- Phone number for contact
    otp_code        TEXT NOT NULL,           -- Random 4-digit code like '5821'
    status          TEXT DEFAULT 'ACTIVE',   -- 'ACTIVE', 'REDEEMED', 'EXPIRED'
    severity        TEXT DEFAULT 'YELLOW',   -- 'RED', 'YELLOW', 'GREEN'
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,    -- Auto-calculated: created_at + 15/20 minutes
    redeemed_at     TIMESTAMPTZ             -- Set when nurse enters OTP (NULL until then)
);

-- Fast index for the TTL worker to find expired holds
CREATE INDEX IF NOT EXISTS idx_holds_active_expiry
    ON public.holds (status, expires_at)
    WHERE status = 'ACTIVE';

-- Fast index for OTP lookup during check-in
CREATE INDEX IF NOT EXISTS idx_holds_otp_lookup
    ON public.holds (hospital_id, otp_code, status);


-- ============================================================
-- TABLE 3: BLOOD INVENTORY
-- One row per hospital × blood group × component combination.
-- Components: PRBC (Packed Red Blood Cells), Platelets, Plasma
-- ============================================================
CREATE TABLE IF NOT EXISTS public.blood_inventory (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    hospital_id     UUID REFERENCES public.hospitals(id) ON DELETE CASCADE NOT NULL,
    blood_group     TEXT NOT NULL,           -- 'O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'
    component       TEXT NOT NULL,           -- 'PRBC', 'Platelets', 'Plasma'
    units_available INT DEFAULT 0,           -- Ready-to-transfuse units
    units_reserved  INT DEFAULT 0,           -- Currently held/reserved
    is_trauma_ready BOOLEAN DEFAULT FALSE,   -- Pre-crossmatched for immediate emergency use
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure unique combination of hospital + blood group + component
CREATE UNIQUE INDEX IF NOT EXISTS idx_blood_unique
    ON public.blood_inventory (hospital_id, blood_group, component);


-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- DISABLED because our backend uses the service_role key
-- which bypasses RLS anyway. This avoids silent empty results.
-- ============================================================
ALTER TABLE public.hospitals DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.holds DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.blood_inventory DISABLE ROW LEVEL SECURITY;


-- ============================================================
-- SEED DATA: 12 KOLKATA HOSPITALS
-- Real hospital names with realistic (fictional) bed data
-- ============================================================
INSERT INTO public.hospitals (name, address, latitude, longitude, phone, specialties,
    adult_icu_total, adult_icu_occupied, adult_icu_held,
    pediatric_icu_total, pediatric_icu_occupied, pediatric_icu_held,
    cardiac_icu_total, cardiac_icu_occupied, cardiac_icu_held,
    general_ward_total, general_ward_occupied, general_ward_held)
VALUES
    -- 1. Premier Government Hospital
    ('SSKM Hospital (PG Hospital)',
     'AJC Bose Road, Bhowanipore, Kolkata 700020',
     22.5355, 88.3438, '033-22041101',
     ARRAY['trauma','cardiac','general','maternity'],
     14, 10, 1,   6, 4, 0,   8, 6, 1,   45, 34, 2),

    -- 2. Major Trauma Centre
    ('NRS Medical College & Hospital',
     'AJC Bose Road, Sealdah, Kolkata 700014',
     22.5584, 88.3629, '033-22653210',
     ARRAY['trauma','general','maternity'],
     12, 9, 0,   5, 3, 0,   0, 0, 0,   50, 38, 1),

    -- 3. Private Super-Speciality
    ('Apollo Gleneagles Hospital',
     'Canal Circular Road, Kadapara, Kolkata 700054',
     22.5117, 88.3953, '033-23203040',
     ARRAY['cardiac','trauma','general'],
     18, 12, 2,   6, 4, 1,   12, 8, 0,   30, 22, 0),

    -- 4. Heart Institute
    ('Rabindranath Tagore International Institute of Cardiac Sciences (RTIICS)',
     'Mukundapur, EM Bypass, Kolkata 700099',
     22.5047, 88.3963, '033-66564444',
     ARRAY['cardiac','general'],
     10, 6, 0,   3, 2, 0,   15, 11, 1,   20, 14, 0),

    -- 5. Large Private Hospital
    ('Fortis Hospital Anandapur',
     'Anandapur, EM Bypass, Kolkata 700107',
     22.5115, 88.4029, '033-66284444',
     ARRAY['trauma','cardiac','general','maternity'],
     16, 11, 1,   7, 5, 0,   10, 7, 0,   35, 26, 2),

    -- 6. Heritage Hospital
    ('Calcutta Medical College & Hospital',
     'College Street, Kolkata 700073',
     22.5726, 88.3639, '033-22413636',
     ARRAY['general','cardiac','maternity'],
     10, 7, 0,   5, 4, 1,   6, 4, 0,   40, 32, 1),

    -- 7. Government General Hospital
    ('RG Kar Medical College & Hospital',
     'Belgachia, Kolkata 700004',
     22.5897, 88.3709, '033-25574440',
     ARRAY['trauma','general','maternity'],
     8, 6, 0,   4, 3, 0,   0, 0, 0,   42, 35, 3),

    -- 8. Multi-Speciality Private
    ('Medica Superspecialty Hospital',
     'Mukundapur, EM Bypass, Kolkata 700099',
     22.5025, 88.3988, '033-66520000',
     ARRAY['general','trauma','cardiac'],
     12, 8, 1,   4, 3, 0,   8, 6, 0,   28, 20, 0),

    -- 9. Maternity & Child Speciality
    ('Institute of Child Health',
     'Park Circus, Kolkata 700017',
     22.5388, 88.3601, '033-22877590',
     ARRAY['maternity','general'],
     4, 3, 0,   10, 7, 1,   0, 0, 0,   25, 18, 2),

    -- 10. Private Multi-Speciality
    ('AMRI Hospital Dhakuria',
     'Dhakuria, Gariahat, Kolkata 700029',
     22.5098, 88.3567, '033-66260000',
     ARRAY['cardiac','trauma','general'],
     10, 7, 1,   4, 2, 0,   7, 5, 1,   22, 16, 0),

    -- 11. Govt. Speciality Hospital
    ('Bangur Institute of Neurosciences',
     'Gobra, Kolkata 700025',
     22.5413, 88.3773, '033-24758252',
     ARRAY['trauma','general'],
     6, 4, 0,   2, 1, 0,   4, 3, 0,   18, 12, 1),

    -- 12. Modern Private Hospital
    ('Peerless Hospitex Hospital',
     'Panchasayar, EM Bypass, Kolkata 700094',
     22.4862, 88.3929, '033-24625000',
     ARRAY['general','cardiac'],
     8, 5, 0,   3, 2, 0,   6, 4, 0,   20, 14, 1),

    -- 13. Tata Medical Center (Newtown Action Area I)
    ('Tata Medical Center',
     '14 MAR(EW), Action Area I, Newtown, Rajarhat, Kolkata 700156',
     22.5714, 88.4735, '033-6605-7000',
     ARRAY['oncology','trauma','general','pediatric','radiology'],
     40, 28, 2,   15, 10, 1,   12, 8, 1,   250, 185, 5),

    -- 14. Ohio Hospital & Diabetes Centre (Newtown Action Area II near Amity)
    ('Ohio Hospital & Diabetes Centre',
     'Plot No. DG-6, Action Area II, Newtown (near Amity University), Kolkata 700161',
     22.5810, 88.4780, '033-6616-6000',
     ARRAY['general','endocrinology','cardiac','orthopedics','diabetology'],
     25, 17, 1,   8, 5, 0,   12, 8, 1,   120, 85, 3),

    -- 15. Bhagirathi Neotia Woman & Child Care (Newtown)
    ('Bhagirathi Neotia Woman & Child Care Centre',
     'Premises No. 27-0327, Street No. 327, Action Area I, Newtown, Kolkata 700156',
     22.5775, 88.4635, '033-6640-5000',
     ARRAY['maternity','pediatric','gynecology','general'],
     15, 10, 1,   30, 21, 2,   5, 3, 0,   140, 100, 4),

    -- 16. HCG EKO Cancer Centre (Newtown)
    ('HCG EKO Cancer Centre',
     'Plot No. DG-4, Action Area II, Newtown, Kolkata 700156',
     22.5792, 88.4680, '033-6655-0000',
     ARRAY['oncology','radiology','general','neurosurgery'],
     20, 14, 1,   8, 5, 0,   8, 5, 0,   110, 78, 3),

    -- 17. Glocal Hospital Newtown (Newtown Action Area II)
    ('Glocal Hospital Newtown',
     'Action Area II, Newtown, Kolkata 700156',
     22.5840, 88.4820, '033-3050-0000',
     ARRAY['general','trauma','orthopedics','cardiac'],
     20, 14, 1,   6, 4, 0,   8, 5, 0,   100, 70, 2),

    -- 18. ILS Hospitals Dum Dum (Nagerbazar Mall Road)
    ('ILS Hospitals Dum Dum',
     '1/85 Mall Road, Nagerbazar, Dum Dum, Kolkata 700080',
     22.6215, 88.4120, '033-4031-9000',
     ARRAY['general','trauma','orthopedics','cardiac','urology'],
     35, 25, 2,   12, 8, 1,   15, 10, 1,   180, 130, 4),

    -- 19. Apex General Hospital (Nagerbazar Crossing)
    ('Apex General Hospital',
     '124 Jessore Road, Nagerbazar Crossing, Dum Dum, Kolkata 700074',
     22.6240, 88.4170, '033-2560-1200',
     ARRAY['general','trauma','orthopedics','maternity'],
     18, 13, 1,   6, 4, 0,   6, 4, 0,   90, 65, 2),

    -- 20. Spandan Hospital & Diagnostic (Nagerbazar)
    ('Spandan Hospital & Diagnostic',
     '36 Nagerbazar Main Road, Dum Dum, Kolkata 700074',
     22.6205, 88.4150, '033-2551-8888',
     ARRAY['general','cardiac','diagnostics','orthopedics'],
     15, 10, 1,   5, 3, 0,   8, 5, 0,   80, 56, 2),

    -- 21. Dum Dum Municipal Specialized Hospital (Nagerbazar)
    ('Dum Dum Municipal Specialized Hospital',
     '4 Imperial Park, Nagerbazar, Dum Dum, Kolkata 700074',
     22.6230, 88.4110, '033-2550-0000',
     ARRAY['general','maternity','pediatric','trauma'],
     20, 15, 1,   10, 7, 0,   6, 4, 0,   150, 118, 4),

    -- 22. Charnock Hospital (Teghoria / Nagerbazar Emergency Hub)
    ('Charnock Hospital',
     'VIP Road, Teghoria, Major Emergency Hub near Nagerbazar, Kolkata 700157',
     22.6178, 88.4350, '033-4050-0000',
     ARRAY['cardiac','trauma','pulmonology','neurology','general'],
     40, 28, 2,   12, 8, 1,   20, 14, 1,   200, 145, 5),

    -- 23. Matri Sadan Hospital (Dum Dum Nagerbazar)
    ('Matri Sadan Hospital',
     '154 KB Sarani, Nagerbazar, Dum Dum, Kolkata 700080',
     22.6190, 88.4090, '033-2551-0101',
     ARRAY['maternity','pediatric','general'],
     12, 8, 1,   15, 10, 1,   4, 2, 0,   100, 75, 3);


-- ============================================================
-- SEED DATA: BLOOD INVENTORY
-- For top 6 hospitals with common blood groups + components
-- ============================================================

-- SSKM Hospital
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    CASE
        WHEN bg.blood_group IN ('O-', 'O+') THEN floor(random() * 8 + 4)::INT
        ELSE floor(random() * 6 + 2)::INT
    END,
    floor(random() * 3)::INT,
    (bg.blood_group = 'O-' AND comp.component = 'PRBC')  -- O- PRBC always trauma-ready
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name = 'SSKM Hospital (PG Hospital)';

-- Apollo Gleneagles
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    CASE
        WHEN bg.blood_group IN ('O-', 'O+') THEN floor(random() * 10 + 5)::INT
        ELSE floor(random() * 7 + 3)::INT
    END,
    floor(random() * 2)::INT,
    (bg.blood_group = 'O-' AND comp.component = 'PRBC')
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name = 'Apollo Gleneagles Hospital';

-- Fortis Hospital
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    CASE
        WHEN bg.blood_group IN ('O-', 'O+') THEN floor(random() * 9 + 4)::INT
        ELSE floor(random() * 6 + 2)::INT
    END,
    floor(random() * 2)::INT,
    (bg.blood_group IN ('O-', 'O+') AND comp.component = 'PRBC')
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name = 'Fortis Hospital Anandapur';

-- RTIICS (Tagore Heart Institute)
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    floor(random() * 6 + 2)::INT,
    floor(random() * 2)::INT,
    (bg.blood_group = 'O-' AND comp.component = 'PRBC')
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('B+')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name LIKE 'Rabindranath Tagore%';

-- NRS Medical College
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    floor(random() * 7 + 3)::INT,
    floor(random() * 2)::INT,
    (bg.blood_group = 'O-' AND comp.component = 'PRBC')
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name LIKE 'NRS Medical%';

-- Medica Superspecialty
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    floor(random() * 8 + 3)::INT,
    floor(random() * 2)::INT,
    (bg.blood_group = 'O-' AND comp.component = 'PRBC')
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name LIKE 'Medica Super%';

-- Newtown & Nagerbazar Hospitals Blood Inventory
INSERT INTO public.blood_inventory (hospital_id, blood_group, component, units_available, units_reserved, is_trauma_ready)
SELECT h.id, bg.blood_group, comp.component,
    CASE
        WHEN bg.blood_group IN ('O-', 'O+') THEN floor(random() * 10 + 5)::INT
        ELSE floor(random() * 6 + 2)::INT
    END,
    floor(random() * 2)::INT,
    (bg.blood_group = 'O-' AND comp.component = 'PRBC')
FROM public.hospitals h
CROSS JOIN (VALUES ('O-'), ('O+'), ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-')) AS bg(blood_group)
CROSS JOIN (VALUES ('PRBC'), ('Platelets'), ('Plasma')) AS comp(component)
WHERE h.name IN (
    'Tata Medical Center',
    'Ohio Hospital & Diabetes Centre',
    'Bhagirathi Neotia Woman & Child Care Centre',
    'HCG EKO Cancer Centre',
    'Glocal Hospital Newtown',
    'ILS Hospitals Dum Dum',
    'Apex General Hospital',
    'Spandan Hospital & Diagnostic',
    'Dum Dum Municipal Specialized Hospital',
    'Charnock Hospital',
    'Matri Sadan Hospital'
);


-- ============================================================
-- VERIFICATION QUERIES (Optional - run after seeding)
-- ============================================================
-- SELECT name, adult_icu_total, adult_icu_occupied, adult_icu_held FROM public.hospitals;
-- SELECT h.name, bi.blood_group, bi.component, bi.units_available FROM public.blood_inventory bi JOIN public.hospitals h ON h.id = bi.hospital_id LIMIT 20;
-- SELECT COUNT(*) as total_hospitals FROM public.hospitals;
-- SELECT COUNT(*) as total_blood_records FROM public.blood_inventory;

-- ============================================================
-- DONE! Go to Table Editor to verify all data is loaded.
-- ============================================================
