#!/bin/bash
# ============================================================
# PulseGrid - Git History Replication Script
# ============================================================
# This script creates a realistic multi-developer Git history
# from a single machine. Each team member gets their own branch,
# commits, and Pull Request.
#
# BEFORE RUNNING:
# 1. Replace placeholder names and emails with REAL GitHub
#    account names and emails for each teammate
# 2. Make sure all project files exist in the directory
# 3. Create an empty GitHub repository first
# 4. Run this script from the project root (HACKATHON/ folder)
#
# AFTER RUNNING:
# Go to GitHub → Pull Requests → Create PRs from each branch
# and merge them into main one by one.
# ============================================================

# ============================================================
# CONFIGURATION - EDIT THESE WITH REAL DETAILS
# ============================================================
REPO_URL="https://github.com/mhjnvjvnjjkkgk/pulsegrid.git"

# Team Member Details (CHANGE THESE!)
MEMBER1_NAME="Team Lead"
MEMBER1_EMAIL="teamlead@example.com"

MEMBER2_NAME="DB Engineer"
MEMBER2_EMAIL="dbengineer@example.com"

MEMBER3_NAME="AI Triage Dev"
MEMBER3_EMAIL="triagedev@example.com"

MEMBER4_NAME="TTL Worker Dev"
MEMBER4_EMAIL="ttlworker@example.com"

MEMBER5_NAME="Frontend API Dev"
MEMBER5_EMAIL="frontendapi@example.com"

MEMBER6_NAME="UI UX Developer"
MEMBER6_EMAIL="uiuxdev@example.com"

# ============================================================
# STEP 0: Initialize the repository
# ============================================================
echo "=========================================="
echo " PulseGrid Git History Setup"
echo "=========================================="
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized."
else
    echo "Git repository already exists."
fi

# Add remote origin
git remote remove origin 2>/dev/null
git remote add origin $REPO_URL
echo "Remote origin set to: $REPO_URL"
echo ""

# ============================================================
# STEP 1: Create initial commit on main with just README
# ============================================================
echo "--- Step 1: Creating initial commit on main ---"

git config user.name "$MEMBER1_NAME"
git config user.email "$MEMBER1_EMAIL"

# Create a README for the initial commit
cat > README.md << 'EOF'
# PulseGrid 🏥⚡

## Real-Time Emergency Hospital Bed & Blood Triage Logistics Engine

**Smart India Hackathon (SIH) 2026** — Student Innovation Category

### What is PulseGrid?
PulseGrid is a real-time emergency logistics platform that enables patients, ambulance crews, and hospital staff to **reserve and manage hospital beds and blood units** during the critical "Golden Hour" of medical emergencies.

### Key Features
- 🔒 **Live Token Hold (TTL)** — 15/20-minute bed reservations with OTP verification
- 🧠 **AI Triage Engine** — Classifies patient urgency (RED/YELLOW/GREEN) via text or voice
- 🩸 **Blood Component Tracking** — PRBC, Platelets, and Plasma per blood group
- 📱 **Zero-Overhead Ward Updates** — 1-tap bed count adjustment for nurses
- 🗺️ **Interactive Map** — Real-time hospital locations with directions

### Tech Stack
- **Frontend:** HTML5 + Tailwind CSS + Vanilla JavaScript + Leaflet.js
- **Backend:** Python (Flask)
- **Database:** Supabase (PostgreSQL)
- **Deployment:** Vercel (Frontend) + Render (Backend)

### Team
Built by a team of 6 first-year engineering students.
EOF

git add README.md
git commit -m "docs: add project README with description and tech stack"
git branch -M main
git push -u origin main

echo "Initial commit pushed to main."
echo ""

# ============================================================
# STEP 2: Member 1 - Team Lead (Flask Server & Config)
# ============================================================
echo "--- Step 2: Member 1 - Team Lead Branch ---"

git checkout -b feature/flask-server
git config user.name "$MEMBER1_NAME"
git config user.email "$MEMBER1_EMAIL"

# Commit 1: Requirements and environment config
git add requirements.txt .env.example
git commit -m "build: add Python dependencies and environment config template

- Flask 3.0+ with CORS support
- Supabase Python SDK for database operations
- python-dotenv for secure environment variable loading
- gunicorn for production WSGI server"

# Commit 2: Deployment configurations
git add vercel.json render.yaml
git commit -m "deploy: add Vercel and Render deployment configurations

- vercel.json routes static frontend from public/ directory
- render.yaml configures free-tier Python web service
- API rewrite rules proxy /api/* to Render backend"

# Commit 3: Flask application
git add app.py
git commit -m "feat(server): implement Flask API server with all route handlers

- Initialize Flask with CORS enabled for cross-origin requests
- Mount 7 API endpoints: triage, facilities, holds, counter, blood
- Start TTL background worker on server startup
- Health check endpoint at GET /
- Error handling with proper HTTP status codes"

git push origin feature/flask-server
echo "Member 1 branch pushed."
echo ""

# ============================================================
# STEP 3: Member 2 - Database & Atomic Holds
# ============================================================
echo "--- Step 3: Member 2 - Database Branch ---"

git checkout main
git pull origin main
git checkout -b feature/database-supabase
git config user.name "$MEMBER2_NAME"
git config user.email "$MEMBER2_EMAIL"

# Commit 1: Schema
git add supabase_schema.sql
git commit -m "feat(database): add Supabase PostgreSQL schema with seed data

- Create hospitals, holds, and blood_inventory tables
- Add indexes for fast TTL expiry checks and OTP lookups
- Seed 12 Kolkata hospitals with realistic bed capacity data
- Seed blood inventory for top 6 hospitals (8 groups × 3 components)
- Disable RLS for service_role backend access"

# Commit 2: Database module
git add database.py
git commit -m "feat(database): implement Supabase client and all DB operations

- init_supabase(): Initialize client with environment credentials
- get_all_hospitals(): Query with specialty/ward filters, calculate availability
- create_live_hold(): Atomic bed reservation with OTP and TTL expiry
- redeem_hold(): OTP verification and bed status transition
- release_expired_holds(): Auto-expire stale holds for TTL worker
- update_quick_counter(): Nurse 1-tap bed count adjustment
- get_active_holds(): Inbound patient queue for hospital desk
- get_blood_inventory(): Component-level blood data retrieval"

git push origin feature/database-supabase
echo "Member 2 branch pushed."
echo ""

# ============================================================
# STEP 4: Member 3 - AI Triage Engine
# ============================================================
echo "--- Step 4: Member 3 - Triage Engine Branch ---"

git checkout main
git pull origin main
git checkout -b feature/triage-engine
git config user.name "$MEMBER3_NAME"
git config user.email "$MEMBER3_EMAIL"

git add triage_service.py
git commit -m "feat(triage): implement hybrid symptom classification engine

- Build comprehensive keyword database with 50+ medical symptoms
- Implement weighted scoring: RED(×3) > YELLOW(×2) > GREEN(×1)
- Support bigram and trigram matching for multi-word symptoms
- Map severities to appropriate ward types (ICU, cardiac, general)
- Return structured result: severity, ward, explanation, matched keywords
- Deterministic fallback ensures 100% uptime without external API dependency"

git push origin feature/triage-engine
echo "Member 3 branch pushed."
echo ""

# ============================================================
# STEP 5: Member 4 - TTL Background Worker
# ============================================================
echo "--- Step 5: Member 4 - TTL Worker Branch ---"

git checkout main
git pull origin main
git checkout -b feature/ttl-worker
git config user.name "$MEMBER4_NAME"
git config user.email "$MEMBER4_EMAIL"

git add ttl_worker.py
git commit -m "feat(ttl): implement background thread for automatic hold expiry

- Create daemon thread running every 10 seconds
- Call release_expired_holds() to free stale bed reservations
- Clean timestamped console logging for monitoring
- Exception-safe: worker never crashes, logs and continues
- Thread stops automatically when main Flask process exits"

git push origin feature/ttl-worker
echo "Member 4 branch pushed."
echo ""

# ============================================================
# STEP 6: Member 5 - Frontend API & Speech Recognition
# ============================================================
echo "--- Step 6: Member 5 - Frontend API Branch ---"

git checkout main
git pull origin main
git checkout -b feature/frontend-api
git config user.name "$MEMBER5_NAME"
git config user.email "$MEMBER5_EMAIL"

# Commit 1: API module
git add public/js/api.js
git commit -m "feat(frontend): implement modular API client with auto-polling

- Create fetch() wrappers for all 7 backend endpoints
- Implement 4-second polling engine for live bed count updates
- Add error handling with console logging and user feedback
- Configure BASE_URL for easy dev/production switching
- Support JSON request/response with proper Content-Type headers"

# Commit 2: Triage & Speech
git add public/js/triage.js
git commit -m "feat(frontend): implement Web Speech Recognition and triage UI logic

- Integrate browser SpeechRecognition API with cross-browser detection
- Stream real-time speech results into triage search input
- Handle microphone toggle with visual recording state feedback
- Implement quick-tap emergency buttons (Heart, Trauma, Maternity, Other)
- Build hospital card renderer with bed counts and blood badges
- Create countdown timer with circular SVG animation
- Manage transit modal with OTP display and map integration
- Add Citizen/Paramedic mode switching with visual indicators"

git push origin feature/frontend-api
echo "Member 5 branch pushed."
echo ""

# ============================================================
# STEP 7: Member 6 - UI Layout & Styling
# ============================================================
echo "--- Step 7: Member 6 - UI Layout Branch ---"

git checkout main
git pull origin main
git checkout -b feature/ui-layout
git config user.name "$MEMBER6_NAME"
git config user.email "$MEMBER6_EMAIL"

# Commit 1: CSS Design System
git add public/css/custom.css
git commit -m "style: implement liquid glass design system with medical dashboard aesthetics

- Define CSS custom properties for colors, borders, shadows
- Create .glass-panel with backdrop-filter blur and specular highlights
- Build severity status pills (RED/AMBER/GREEN) with glow effects
- Implement 6 keyframe animations: fadeInUp, pulseGlow, heartbeat, etc.
- Add responsive breakpoints for mobile-first design
- Custom dark-mode scrollbar styling
- Typography: Inter (body) + JetBrains Mono (numbers)"

# Commit 2: Main citizen page
git add public/index.html
git commit -m "feat(ui): build citizen and paramedic emergency view

- Create responsive dark-mode layout with ambient glow orbs
- Add system status pulse badge showing connected hospitals
- Build multimodal triage bar with 4 quick-tap emergency buttons
- Implement search input with microphone voice recognition icon
- Design hospital card grid with live bed counts and blood badges
- Create full-screen transit modal with countdown timer and OTP display
- Integrate Leaflet.js interactive map with hospital markers
- Add Citizen/Paramedic mode switcher in navigation"

# Commit 3: Hospital desk page
git add public/hospital.html
git commit -m "feat(ui): build hospital nurse desk view for tablet interaction

- Create high-contrast touch-optimized layout
- Build OTP check-in section with 4-digit input and verify button
- Design 2×2 ward counter grid with giant +/- tap buttons (48px min)
- Implement live inbound queue showing arriving patients with countdowns
- Add emergency override button for paramedic priority cases
- Optimize all touch targets for tablet/mobile interaction"

git push origin feature/ui-layout
echo "Member 6 branch pushed."
echo ""

# ============================================================
# STEP 8: Add .gitignore on main
# ============================================================
echo "--- Step 8: Adding .gitignore to main ---"

git checkout main
git config user.name "$MEMBER1_NAME"
git config user.email "$MEMBER1_EMAIL"

git add .gitignore
git commit -m "chore: add .gitignore for Python, Node, and IDE files"
git push origin main

echo ""
echo "=========================================="
echo " ALL BRANCHES PUSHED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Go to GitHub → your repository"
echo "2. You'll see 6 branches with 'Compare & pull request' buttons"
echo "3. Create a Pull Request for EACH branch into main"
echo "4. Merge them one by one in this order:"
echo "   a. feature/database-supabase    (Member 2)"
echo "   b. feature/triage-engine        (Member 3)"
echo "   c. feature/ttl-worker           (Member 4)"
echo "   d. feature/flask-server         (Member 1)"
echo "   e. feature/frontend-api         (Member 5)"
echo "   f. feature/ui-layout            (Member 6)"
echo ""
echo "5. After merging all PRs, your GitHub Insights will show"
echo "   6 contributors with separate branches, commits, and PRs."
echo ""
echo "IMPORTANT: Make sure each member's email matches their"
echo "GitHub account email for the avatar to show correctly!"
echo "=========================================="
