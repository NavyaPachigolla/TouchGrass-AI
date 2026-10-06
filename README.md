# 🌱 TouchGrass AI – Offline Outdoor Adventure Planner

> **"Let AI plan it. You go outside."**  
> *A local, privacy-first outdoor adventure generator built for the **Hacktoberfest Open-Source AI Challenge – Week 1 ("Touch Grass")**.*

---

## 📌 What I Built

Modern life is overwhelmed by digital notifications, endless social scrolling, and persistent screen fatigue. While artificial intelligence is often deployed to keep users glued to feeds and chat boxes, **TouchGrass AI flips the paradigm**:

**TouchGrass AI uses artificial intelligence exclusively as a catalyst to get you off your screen and into the physical world.**

With TouchGrass AI, you spend **60 seconds** configuring your outdoor context:
- Your activity (Walking, Photography, Nature exploration, Gardening, Bird watching, etc.)
- Your available time (15m, 30m, 45m, 1h, 2h)
- Your energy level (Low, Medium, High)
- Your surrounding environment (Campus, Park, Neighborhood, Trail, Garden)
- Your companions (Solo, Friends, Family, Run club)
- Your location context (e.g., *"College campus quad with mature oak trees and a small pond"*)

A **locally running open-weight model** (`Qwen2.5 3B Instruct` via Ollama) formulates a structured, safe, sensory-rich outdoor mission containing:
1. An adventurous mission title and inspiring description
2. 4–7 actionable, non-digital steps
3. A gear packing checklist
4. Tailored outdoor safety guidance
5. A **Screen-Off Challenge** (e.g., *"Lock phone in your pocket on Do Not Disturb for 30 minutes"*)

Once generated, hitting the **"GO OUTSIDE 🌱"** button shifts the application into a minimalist countdown timer with a direct mandate:
> **"Your mission has started. Put your phone away. Touch grass."**

---

## 🎥 Demo

<!-- DEMO VIDEO / GIF PLACEHOLDER -->
> *Placeholder: Insert your recorded demo GIF or video walkthrough here (`docs/touchgrass-demo.gif` or YouTube link).*

```
+-----------------------------------------------------------------------------------+
|  [DEMO PLACEHOLDER: GIF showing prompt input -> local AI generation -> Go Outside]|
+-----------------------------------------------------------------------------------+
```

### Try Live Demo Presets
The web interface features 1-click preset buttons for immediate exploration:
- **🎓 15m Campus Hunt:** Quick between-class recharge for university students
- **🏡 30m Neighborhood Walk:** Mindful suburban sensory stroll
- **📷 45m Photo Walk:** Macro texture & lighting safari
- **🌲 1h Trail Trek:** Screen-free group exploration quest
- **🌻 30m Gardening:** Hands-in-the-dirt earthing mission

---

## 📂 Code & Repository Structure

```
week-1/
├── app.py                     # Flask backend, Ollama API orchestrator, fallback generator
├── requirements.txt           # Minimal Python dependencies (Flask, requests)
├── README.md                  # Comprehensive documentation and developer guide
├── .gitignore                 # Clean repository exclusions
│
├── prompts/
│   └── outdoor_mission_prompt.txt # Robust system prompt with safety & JSON schema guardrails
│
├── templates/
│   └── index.html             # Responsive, nature-inspired semantic HTML5 template
│
└── static/
    ├── style.css              # Earth-toned palette, glassmorphism cards, zen mode UI
    └── script.js              # Ollama health checks, preset loader, countdown timer
```

---

## 🛠️ How I Built It

### 1. Minimalist, Fast Tech Stack
- **Backend:** Python + Flask. Ultra-lightweight, zero bloat, easy to run on any laptop.
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript. No bulky JavaScript frameworks or build steps required.
- **Local AI Engine:** [Ollama](https://ollama.com/) running **Qwen2.5 3B Instruct** locally.
- **Protocol:** HTTP REST via Ollama's local endpoint (`http://localhost:11434/api/generate`).

### 2. Prompt Engineering & Strict JSON Response Handling
The system prompt in [`prompts/outdoor_mission_prompt.txt`](prompts/outdoor_mission_prompt.txt) enforces:
- Grounded outdoor activities that require **no phone interaction** during execution.
- Strict safety constraints: no trespassing, no hazardous structures, awareness of public boundaries, hydration alerts.
- Ollama's `format: "json"` mode guarantees clean, deterministic JSON parsing directly into native Python dictionaries, safely handling edge cases without markdown syntax disruptions.

### 3. Graceful Offline Fallback
If Ollama is not installed or currently stopped, TouchGrass AI automatically detects the offline status, provides instructions on how to start Ollama, and engages a local offline rule-based mission planner so testing and exploration never break.

---

## 💡 Why Open Innovation Matters

This project demonstrates the unique power of **open-weight models and local AI**:

1. **100% Local Inference:**  
   The model runs entirely on your device's CPU/GPU. You do not need an account, an API key, or a credit card to generate missions.
2. **True Disconnection & Zero Cloud Data:**  
   Your personal habits, location details, schedule availability, and energy levels never leave your local machine. Closed commercial AI APIs log prompts and user telemetry—TouchGrass AI keeps your life completely private.
3. **No Vendor Lock-In:**  
   Because the system interfaces with standard open-weight inference runners (Ollama), developers can freely swap `Qwen2.5 3B` for `Llama 3`, `Mistral`, `Gemma 2`, or a quantized fine-tuned model without rewriting backend logic.
4. **Small Open-Weight Models Excel at Focused Tasks:**  
   You do not need a multi-billion-parameter cloud frontier model costing millions of dollars to plan a 30-minute nature walk. A compact **3B open-weight model** runs in seconds on consumer laptops with minimal RAM and battery impact.
5. **Sustainable & Resilient:**  
   The app works in remote cabins, national parks, or areas with poor internet connectivity—the exact places where people want to touch grass!

---

## 🔐 Privacy Guarantee

- **No Remote Telemetry:** No user analytics or tracking scripts.
- **No Third-Party APIs:** No requests are sent to closed proprietary AI APIs (OpenAI, Anthropic, Google Cloud, etc.).
- **Zero Data Retention:** Prompts are processed ephemerally in local memory and are never persisted to external servers.

---

## 🚀 Running Locally

Follow these quick steps to get TouchGrass AI running on your machine:

### 1. Prerequisites
- **Python 3.10+** installed
- **Ollama** installed ([Download Ollama](https://ollama.com/download))

### 2. Install & Start the Local Open-Weight Model
Open your terminal and run:
```bash
ollama run qwen2.5:3b
```
*(Ollama will download the lightweight ~1.9 GB model and load it locally).*

### 3. Clone & Setup Repository
```bash
git clone https://github.com/your-username/touchgrass-ai.git
cd touchgrass-ai
```

### 4. Create Virtual Environment & Install Dependencies
```bash
# Optional: Create and activate a virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 5. Launch the Application
```bash
python app.py
```

### 6. Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```
You will see the green status badge: **`Local AI: qwen2.5:3b (Online)`**.  
Pick your parameters, hit **"Generate My Outdoor Mission"**, and then click **"GO OUTSIDE 🌱"**!

---

## 📸 Screenshots

<!-- SCREENSHOTS PLACEHOLDER -->
### 1. Configure Outdoor Mission
> *Placeholder: Add screenshot of the nature-inspired form interface.*

### 2. Structured Local AI Mission Output
> *Placeholder: Add screenshot of the generated outdoor mission cards.*

### 3. Screen-Off "GO OUTSIDE" Zen Mode
> *Placeholder: Add screenshot of the minimal screen-off countdown screen.*

---

## 🍂 Hacktoberfest Week 1: "Touch Grass" Alignment

| Challenge Requirement | How TouchGrass AI Fulfills It |
|---|---|
| **Open-Weight / Open-Source AI** | Powered by `Qwen2.5 3B Instruct` via local Ollama inference. 100% open source. |
| **Gets people off the screen** | The application is intentionally designed so the screen is **only used for 60 seconds of planning**. |
| **Into the physical world** | Every mission provides physical world steps (sensory observation, walking, breathing, physical movement). |
| **Screen-Off Challenge** | Features dedicated disconnect challenges and a zen countdown screen instructing the user to pocket their device. |

---

## 📋 Example Generated Missions

Judges and developers can review these actual generated missions:

### Example 1: 15-Minute Campus Nature Hunt
- **Context:** College campus quad with lawn, mature oak trees, and stone benches
- **Mission:** Campus Canopy Quick Hunt
- **Steps:**
  1. Leave your study desk, slide your phone into your backpack, and walk out to the quad.
  2. Find the oldest tree on campus and stand beneath its canopy.
  3. Locate 3 leaves with completely different margins (smooth, serrated, lobed).
  4. Sit on a stone bench for 2 full minutes with closed eyes, counting natural campus sounds.
  5. Take one final deep breath of open air before returning with renewed focus.
- **What to bring:** Curiosity and comfortable shoes.
- **Screen-Off Challenge:** Do not pull out your phone once between leaving your desk and returning.

### Example 2: 30-Minute Neighborhood Walking Challenge
- **Context:** Quiet residential neighborhood with tree-lined sidewalks
- **Mission:** 30-Minute Suburban Sound & Solitude Stroll
- **Steps:**
  1. Step outside your front door, lock your phone screen, and place it in your back pocket.
  2. Walk 10 minutes in a direction you rarely take on your standard route.
  3. Count how many different flower colors you can spot in front yard gardens.
  4. Pause at a neighborhood park or open corner to stretch your shoulders and neck.
  5. Walk the remaining 10 minutes home practicing rhythmic, slow breathing.
- **What to bring:** Water bottle, sun hat, and walking shoes.
- **Screen-Off Challenge:** Lock your screen for the entire 30 minutes without checking notifications.

### Example 3: 45-Minute Photography Walk
- **Context:** City park with pond and wooded trails
- **Mission:** Golden Hour Texture & Ripple Safari
- **Steps:**
  1. Put phone in Do Not Disturb. Walk 10 minutes observing light reflections without snapping any photos.
  2. Find an interesting water reflection or sunlight filtering through leaves.
  3. Frame exactly two macro shots of plant veins, wood grain, or rock moss.
  4. Find a low-angle composition that makes an ordinary park element look grand.
  5. Put your camera away for the final 15 minutes and enjoy the view purely through your own eyes.
- **What to bring:** Camera or phone with clean lens, water, and sunglasses.
- **Screen-Off Challenge:** Strict 5-shutter limit: evaluate each frame before snapping.

### Example 4: 1-Hour Friend Exploration Mission
- **Context:** Wooded nature reserve trail with moderate inclines
- **Mission:** The Wildwood Trail Landmark Quest
- **Steps:**
  1. Everyone silences their devices and designates one emergency pack for phones.
  2. Hike 15 minutes along the main trail to the first trail marker or overlook.
  3. Challenge: Each person must identify one animal track, bird call, or unusual rock formation.
  4. Take a 10-minute sit-down break at a scenic overlook—chat without any screens present.
  5. Take the loop trail back at a brisk pace, comparing your favorite outdoor observations.
- **What to bring:** Water for each person, trail snacks, comfortable hiking footwear.
- **Screen-Off Challenge:** All phones in backpacks—first person who checks social media buys snacks afterwards!

### Example 5: Beginner Gardening Mission
- **Context:** Backyard garden patch or patio planters
- **Mission:** Garden Bed Revitalization & Soil Grounding
- **Steps:**
  1. Place your phone safely indoors on a charger. Step into the garden with bare hands.
  2. Check soil moisture by pressing your finger two inches into the dirt.
  3. Weed gently around 5 companion plants, pulling from the taproot.
  4. Clear yellowed lower leaves to allow sunlight and airflow to the stems.
  5. Water gently at the roots, watching the dry soil drink the moisture.
  6. Stand quietly for 2 minutes admiring the refreshed greenery.
- **What to bring:** Hand trowel, watering can or hose, gardening gloves if preferred.
- **Screen-Off Challenge:** Complete the entire gardening cycle with your phone remaining inside the house.

---

## 🔮 Future Improvements

- [ ] **Hyper-Local Weather Forecast Integration:** Auto-detect UV index and rain probability without cloud tracking.
- [ ] **OpenStreetMap & Trail Geo-Coordinates:** Integrate local public park boundaries and open greenway trails.
- [ ] **Audio/Voice Briefing Mode:** Listen to the mission read aloud once, eliminating reading the screen entirely.
- [ ] **Smartwatch Companion App:** Subtle haptic buzzes when step timers expire while keeping screens black.
- [ ] **PWA / Offline Mobile Version:** Install directly on mobile home screens as a lightweight standalone web app.

---

## 📜 License
MIT License. Free and open source for the community.
