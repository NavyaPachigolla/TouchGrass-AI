import os
import sys
import json
import logging
import requests
from flask import Flask, render_template, request, jsonify

# Windows terminal encoding safety
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TouchGrassAI")

app = Flask(__name__)

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
PREFERRED_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "outdoor_mission_prompt.txt")


def load_prompt_template() -> str:
    """Load the system prompt template from disk."""
    try:
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Could not read prompt file: {e}")
    # Fallback inline template
    return (
        "You are TouchGrass AI, an outdoor adventure planner. "
        "Create a safe, structured outdoor activity to get the user off their phone. "
        "Activity: {activity}, Time: {time}, Energy: {energy}, Environment: {environment}, "
        "Company: {company}, Interest: {interest}, Context: {context}. "
        "Return JSON only with: mission_title, short_description, estimated_duration, difficulty, "
        "steps (list of 4-7 steps), what_to_bring, safety_note, screen_off_challenge."
    )


def get_ollama_status():
    """Check if Ollama is running and inspect available models."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            
            # Determine active model: preferred, or match prefix, or first available
            active_model = PREFERRED_MODEL
            if models:
                if PREFERRED_MODEL in models:
                    active_model = PREFERRED_MODEL
                elif any(m.startswith("qwen2.5") for m in models):
                    active_model = next(m for m in models if m.startswith("qwen2.5"))
                elif any("llama3" in m for m in models):
                    active_model = next(m for m in models if "llama3" in m)
                else:
                    active_model = models[0]

            return {
                "online": True,
                "models": models,
                "active_model": active_model,
                "host": OLLAMA_HOST
            }
    except Exception as e:
        logger.debug(f"Ollama health check failed: {e}")

    return {
        "online": False,
        "models": [],
        "active_model": PREFERRED_MODEL,
        "host": OLLAMA_HOST
    }


def clean_json_response(raw_text: str) -> dict:
    """Extract and parse JSON safely from model output."""
    text = raw_text.strip()

    # Strip code block wrappers if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Locate first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace : last_brace + 1]

    parsed = json.loads(text)

    # Normalize keys if the model varied capitalization or naming
    normalized = {
        "mission_title": (
            parsed.get("mission_title")
            or parsed.get("title")
            or parsed.get("name")
            or "Outdoor Grass Exploration"
        ),
        "short_description": (
            parsed.get("short_description")
            or parsed.get("description")
            or parsed.get("summary")
            or "A mindful mission to step away from screens and explore the physical world."
        ),
        "estimated_duration": (
            parsed.get("estimated_duration")
            or parsed.get("duration")
            or "30 minutes"
        ),
        "difficulty": (
            parsed.get("difficulty")
            or parsed.get("level")
            or "Easy"
        ),
        "steps": parsed.get("steps") or parsed.get("tasks") or [],
        "what_to_bring": (
            parsed.get("what_to_bring")
            or parsed.get("gear")
            or parsed.get("items")
            or "Comfortable shoes and a water bottle."
        ),
        "safety_note": (
            parsed.get("safety_note")
            or parsed.get("safety")
            or "Stay aware of your surroundings and respect public boundaries."
        ),
        "screen_off_challenge": (
            parsed.get("screen_off_challenge")
            or parsed.get("challenge")
            or "Put your phone on silent and leave it in your pocket for the entire duration."
        )
    }

    # Ensure steps is a non-empty list of strings
    if isinstance(normalized["steps"], list) and len(normalized["steps"]) > 0:
        normalized["steps"] = [str(s).strip() for s in normalized["steps"] if str(s).strip()]
    else:
        normalized["steps"] = [
            "1. Step outside and take three deep breaths of fresh outdoor air.",
            "2. Walk 5 minutes without looking at your phone.",
            "3. Find three different natural objects or plant varieties.",
            "4. Pause and listen silently for bird calls or natural sounds.",
            "5. Walk back via an alternative path and celebrate touching grass!"
        ]

    return normalized


def generate_fallback_mission(params: dict) -> dict:
    """
    Curated offline fallback mission generator.
    Activated gracefully if Ollama is stopped or unavailable.
    """
    activity = params.get("activity", "Walking")
    time_str = params.get("time", "30 minutes")
    energy = params.get("energy", "Medium")
    env = params.get("environment", "Park")
    company = params.get("company", "Solo")
    interest = params.get("interest", "Nature")
    context = params.get("context", "").strip()

    loc_name = f"around {context}" if context else f"in the {env.lower()}"

    templates = {
        "Walking": {
            "title": f"The Mindful {time_str} {env} Loop",
            "desc": f"A refreshing screen-free stroll {loc_name} focused on sensory discovery.",
            "steps": [
                "1. Step out the door, slip your phone into 'Do Not Disturb', and pocket it.",
                f"2. Walk at a steady pace toward the greenest section {loc_name}.",
                "3. Spot 4 distinct textures in nature (rough bark, smooth stone, soft moss, fragile leaves).",
                "4. Pause in a shaded spot for 3 minutes. Close your eyes and count all distinct ambient sounds.",
                "5. Take a mindful loop back using a path you have never explored before."
            ],
            "bring": "Water bottle and supportive walking sneakers.",
            "safety": "Stay alert at road crossings and stick to well-lit public pathways.",
            "challenge": f"Keep your phone untouched in your pocket for the full {time_str}."
        },
        "Photography": {
            "title": f"Outdoor Light & Texture Photo Trek ({time_str})",
            "desc": f"An observant expedition {loc_name} where you seek perspective instead of notifications.",
            "steps": [
                "1. Lock your phone or digital camera until step 3—first let your naked eyes adjust.",
                f"2. Wander {loc_name} looking specifically for high-contrast shadows and natural patterns.",
                "3. Choose ONE natural element (a budding branch, leaf vein, or rock formation).",
                "4. Compose 3 thoughtful photos from different angles (ground level, eye level, overhead).",
                "5. Put the camera away immediately after taking them and walk back appreciating the scene."
            ],
            "bring": "Camera or phone (set to airplane mode except camera app) and sunglasses.",
            "safety": "Watch your footing while framing shots; never step backward without checking.",
            "challenge": "Maximum 5 total photos allowed during the entire outing—make each one deliberate."
        },
        "Bird watching": {
            "title": f"Canopy Song & Flutter Recon ({time_str})",
            "desc": f"A quiet, focused wildlife observation mission {loc_name}.",
            "steps": [
                "1. Head to the nearest stand of mature trees or bushes.",
                "2. Stand completely still and silent for 3 minutes to let wildlife settle.",
                "3. Scan the upper branches and listen for distinct chirp melodies.",
                "4. Track the flight path of at least one bird without following it through a screen.",
                "5. Note its feather colors, beak shape, and behavior mentally before returning."
            ],
            "bring": "Binoculars if available, water bottle, and neutral-colored outerwear.",
            "safety": "Remain on public paths and avoid disturbing nesting or feeding animals.",
            "challenge": "Zero screen interaction. Your ears and eyes are your only sensors today."
        },
        "Gardening": {
            "title": f"Hands-In-The-Dirt Soil Awakening ({time_str})",
            "desc": f"Grounding physical contact with soil and flora {loc_name}.",
            "steps": [
                "1. Gather your gardening tools and inspect soil moisture with your bare fingers.",
                "2. Clear away dry debris and weed carefully around healthy stems.",
                "3. Aerate or gently loosen compacted soil around plant roots.",
                "4. Water base roots thoroughly without splashing foliage.",
                "5. Take a minute to breathe the fresh scent of moist earth before washing up."
            ],
            "bring": "Gardening gloves, hand trowel, watering can, and sun hat.",
            "safety": "Wear gloves to protect against thorns and wash hands thoroughly after contact.",
            "challenge": "No music or podcasts while your hands are in the soil—enjoy the quiet."
        },
        "Nature exploration": {
            "title": f"Micro-Ecosystem Detective Hunt ({time_str})",
            "desc": f"Discover the miniature worlds hidden in plain sight {loc_name}.",
            "steps": [
                "1. Walk 5 minutes away from indoor structures with your phone silenced.",
                "2. Locate a fallen log, large boulder, or mossy tree trunk.",
                "3. Inspect a single square foot of ground closely for tiny insects, fungi, or seed pods.",
                "4. Collect three fallen non-living items (acorn cap, pinecone, dry leaf) to examine.",
                "5. Return items gently to their natural resting place and take the scenic route home."
            ],
            "bring": "Magnifying glass if you have one, water, and outdoor-ready shoes.",
            "safety": "Look before reaching under logs or stones; respect all wildlife habitats.",
            "challenge": "Keep the screen off for the entire mission duration."
        }
    }

    base = templates.get(activity, templates["Walking"])

    # Adjust difficulty based on energy
    diff = "Easy" if energy == "Low" else ("Moderate" if energy == "Medium" else "Challenging")

    return {
        "mission_title": base["title"],
        "short_description": base["desc"],
        "estimated_duration": time_str,
        "difficulty": diff,
        "steps": base["steps"],
        "what_to_bring": base["bring"],
        "safety_note": base["safety"],
        "screen_off_challenge": base["challenge"]
    }


# Pre-crafted demo missions for offline showcase or instant testing
DEMO_MISSIONS = [
    {
        "id": "campus_nature_hunt",
        "label": "15-Min Campus Nature Hunt",
        "inputs": {
            "activity": "Nature exploration",
            "time": "15 minutes",
            "energy": "Medium",
            "environment": "Campus",
            "company": "Solo",
            "interest": "Nature",
            "context": "College campus quad with lawn, mature oak trees, and stone benches"
        },
        "mission": {
            "mission_title": "Campus Canopy Quick Hunt",
            "short_description": "A high-impact 15-minute sensory break between classes to recharge your focus.",
            "estimated_duration": "15 minutes",
            "difficulty": "Easy",
            "steps": [
                "1. Leave your study desk, slide your phone into your backpack, and walk out to the quad.",
                "2. Find the oldest tree on campus and stand beneath its canopy.",
                "3. Locate 3 leaves with completely different margins (smooth, serrated, lobed).",
                "4. Sit on a stone bench for 2 full minutes with closed eyes, counting natural campus sounds.",
                "5. Take one final deep breath of open air before returning with renewed focus."
            ],
            "what_to_bring": "Just your curiosity and comfortable shoes.",
            "safety_note": "Stay on pedestrian walkways and avoid crossing busy campus bike paths blindly.",
            "screen_off_challenge": "Do not pull out your phone once between leaving your desk and returning."
        }
    },
    {
        "id": "neighborhood_walk",
        "label": "30-Min Neighborhood Walking Challenge",
        "inputs": {
            "activity": "Walking",
            "time": "30 minutes",
            "energy": "Medium",
            "environment": "Neighborhood",
            "company": "Solo",
            "interest": "Relaxation",
            "context": "Quiet residential neighborhood with tree-lined sidewalks"
        },
        "mission": {
            "mission_title": "30-Minute Suburban Sound & Solitude Stroll",
            "short_description": "Break out of four walls and reset your attention span along quiet tree-lined streets.",
            "estimated_duration": "30 minutes",
            "difficulty": "Easy",
            "steps": [
                "1. Step outside your front door, lock your phone screen, and place it in your back pocket.",
                "2. Walk 10 minutes in a direction you rarely take on your standard route.",
                "3. Count how many different flower colors you can spot in front yard gardens.",
                "4. Pause at a neighborhood park or open corner to stretch your shoulders and neck.",
                "5. Walk the remaining 10 minutes home practicing rhythmic, slow breathing."
            ],
            "what_to_bring": "Water bottle, sun hat, and comfortable walking shoes.",
            "safety_note": "Use sidewalks where available, face oncoming traffic if walking in the road, and stay aware.",
            "screen_off_challenge": "Lock your screen for the entire 30 minutes without glancing at notifications."
        }
    },
    {
        "id": "photography_walk",
        "label": "45-Min Photography Walk",
        "inputs": {
            "activity": "Photography",
            "time": "45 minutes",
            "energy": "Medium",
            "environment": "Park",
            "company": "Solo",
            "interest": "Photography",
            "context": "Local park with winding pond trail and wooded edge"
        },
        "mission": {
            "mission_title": "Golden Hour Texture & Ripple Safari",
            "short_description": "Train your biological eyes to see light, shadow, and organic geometry without scrolling.",
            "estimated_duration": "45 minutes",
            "difficulty": "Moderate",
            "steps": [
                "1. Put phone in Do Not Disturb. Walk 10 minutes observing light reflections without snapping any photos.",
                "2. Find an interesting water reflection or sunlight filtering through leaves.",
                "3. Frame exactly two macro shots of plant veins, wood grain, or rock moss.",
                "4. Find a low-angle composition that makes an ordinary park element look grand.",
                "5. Put your camera away for the final 15 minutes and enjoy the view purely through your own eyes."
            ],
            "what_to_bring": "Phone or camera with clean lens, water bottle, and sunglasses.",
            "safety_note": "Mind the water edge and uneven roots while looking through the lens.",
            "screen_off_challenge": "Strict 5-shutter limit: evaluate each frame before snapping, no endless burst shots."
        }
    },
    {
        "id": "friend_exploration",
        "label": "1-Hour Friend Exploration Mission",
        "inputs": {
            "activity": "Nature exploration",
            "time": "1 hour",
            "energy": "High",
            "environment": "Trail",
            "company": "With friends",
            "interest": "Exploration",
            "context": "Wooded nature reserve trail with moderate inclines"
        },
        "mission": {
            "mission_title": "The Wildwood Trail Landmark Quest",
            "short_description": "A collaborative outdoor scouting trek designed for real-time conversation and shared discovery.",
            "estimated_duration": "1 hour",
            "difficulty": "Moderate",
            "steps": [
                "1. Everyone silences their devices and designates one emergency pack for phones.",
                "2. Hike 15 minutes along the main trail to the first trail marker or overlook.",
                "3. Challenge: Each person must identify one animal track, bird call, or unusual rock formation.",
                "4. Take a 10-minute sit-down break at a scenic overlook—chat without any screens present.",
                "5. Take the loop trail back at a brisk pace, comparing your favorite outdoor observations."
            ],
            "what_to_bring": "Water for each person, trail snacks, comfortable hiking footwear.",
            "safety_note": "Stay on marked trails, communicate pace with friends, and leave no trace behind.",
            "screen_off_challenge": "All phones in backpacks—first person who checks social media buys snacks afterwards!"
        }
    },
    {
        "id": "gardening_mission",
        "label": "Beginner Gardening Mission",
        "inputs": {
            "activity": "Gardening",
            "time": "30 minutes",
            "energy": "Low",
            "environment": "Garden",
            "company": "Solo",
            "interest": "Nature",
            "context": "Home backyard garden plot or community garden bed"
        },
        "mission": {
            "mission_title": "Garden Bed Revitalization & Soil Grounding",
            "short_description": "Feel the texture of the living earth and bring life back to your outdoor garden patch.",
            "estimated_duration": "30 minutes",
            "difficulty": "Easy",
            "steps": [
                "1. Place your phone safely indoors on a charger. Step into the garden with bare hands.",
                "2. Check soil moisture by pressing your finger two inches into the dirt.",
                "3. Weed gently around 5 companion plants, pulling from the taproot.",
                "4. Clear yellowed lower leaves to allow sunlight and airflow to the stems.",
                "5. Water gently at the roots, watching the dry soil drink the moisture.",
                "6. Stand quietly for 2 minutes admiring the refreshed greenery."
            ],
            "what_to_bring": "Hand trowel, watering can or hose, gardening gloves if preferred.",
            "safety_note": "Lift with your knees when carrying water buckets and wash hands after soil handling.",
            "screen_off_challenge": "Complete the entire gardening cycle with your phone remaining inside the house."
        }
    }
]


@app.route("/")
def index():
    """Render the main landing page."""
    status = get_ollama_status()
    return render_template(
        "index.html",
        ollama_status=status
    )


@app.route("/api/status", methods=["GET"])
def api_status():
    """Return live status of local Ollama runtime and available models."""
    return jsonify(get_ollama_status())


@app.route("/api/examples", methods=["GET"])
def api_examples():
    """Return pre-crafted demo missions for instant showcase."""
    return jsonify({"examples": DEMO_MISSIONS})


@app.route("/generate", methods=["POST"])
@app.route("/api/generate", methods=["POST"])
def generate_mission():
    """Generate an outdoor mission via local Ollama or fallback generator."""
    payload = request.get_json(silent=True) or {}

    # Extract & validate fields
    activity = str(payload.get("activity", "Walking")).strip()[:50] or "Walking"
    time_avail = str(payload.get("time", "30 minutes")).strip()[:30] or "30 minutes"
    energy = str(payload.get("energy", "Medium")).strip()[:30] or "Medium"
    environment = str(payload.get("environment", "Park")).strip()[:50] or "Park"
    company = str(payload.get("company", "Solo")).strip()[:50] or "Solo"
    interest = str(payload.get("interest", "Nature")).strip()[:50] or "Nature"
    context = str(payload.get("context", "")).strip()[:200]

    user_params = {
        "activity": activity,
        "time": time_avail,
        "energy": energy,
        "environment": environment,
        "company": company,
        "interest": interest,
        "context": context or f"A typical {environment.lower()} environment"
    }

    ollama_info = get_ollama_status()

    # Attempt local open-weight inference if Ollama is online
    if ollama_info["online"]:
        model_name = ollama_info["active_model"]
        raw_prompt = load_prompt_template()

        # Safely replace placeholders without conflicting with JSON schema curly braces
        formatted_prompt = (
            raw_prompt
            .replace("{activity}", user_params["activity"])
            .replace("{time}", user_params["time"])
            .replace("{energy}", user_params["energy"])
            .replace("{environment}", user_params["environment"])
            .replace("{company}", user_params["company"])
            .replace("{interest}", user_params["interest"])
            .replace("{context}", user_params["context"])
        )

        try:
            logger.info(f"Dispatching mission generation to local model: {model_name}")
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model_name,
                    "prompt": formatted_prompt,
                    "format": "json",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 350
                    }
                },
                timeout=100
            )

            if response.status_code == 200:
                resp_json = response.json()
                raw_output = resp_json.get("response", "")
                mission_data = clean_json_response(raw_output)
                
                return jsonify({
                    "success": True,
                    "source": "local_ai",
                    "model": model_name,
                    "open_weight": True,
                    "privacy": "100% Local Inference (Zero Cloud Data)",
                    "mission": mission_data,
                    "inputs": user_params
                })
            else:
                logger.warning(f"Ollama returned non-200 code: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.warning("Local Ollama inference timed out (60s limit). Falling back.")
        except Exception as e:
            logger.warning(f"Local Ollama inference failed with error: {e}")

    # Fallback to local deterministic generator if Ollama is offline or timed out
    logger.info("Using graceful offline fallback outdoor mission generator.")
    fallback_mission = generate_fallback_mission(user_params)

    return jsonify({
        "success": True,
        "source": "fallback",
        "model": "Offline Rule-Based Planner (Ollama offline)",
        "open_weight": True,
        "privacy": "100% Offline Generation",
        "notice": (
            "Local AI is not running yet. Start Ollama and pull qwen2.5:3b to enable "
            "open-weight AI inference. This plan was generated by our offline adventure planner."
        ),
        "mission": fallback_mission,
        "inputs": user_params
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("==================================================")
    print("  TouchGrass AI - Offline Outdoor Adventure Planner")
    print("  Tagline: 'Let AI plan it. You go outside.'")
    print("  Hacktoberfest Week 1: Touch Grass Challenge")
    print(f"  Server listening at: http://127.0.0.1:{port}")
    print("==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
