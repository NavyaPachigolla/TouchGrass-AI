/**
 * TouchGrass AI – Frontend Client Application
 * Hacktoberfest Week 1: Touch Grass Challenge
 * Philosophy: The screen is only used to create the plan. You go outside.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const statusDot = document.getElementById('statusDot');
  const statusLabel = document.getElementById('statusLabel');
  const refreshStatusBtn = document.getElementById('refreshStatusBtn');
  const offlineBanner = document.getElementById('ollamaOfflineBanner');
  const copyCmdBtn = document.getElementById('copyCmdBtn');

  const missionForm = document.getElementById('missionForm');
  const generateBtn = document.getElementById('generateBtn');
  const loadingState = document.getElementById('loadingState');
  const loadingTip = document.getElementById('loadingTip');

  const resultSection = document.getElementById('resultSection');
  const badgeDifficulty = document.getElementById('badgeDifficulty');
  const badgeDuration = document.getElementById('badgeDuration');
  const badgeEnvironment = document.getElementById('badgeEnvironment');
  const badgeAiModel = document.getElementById('badgeAiModel');
  const missionTitle = document.getElementById('missionTitle');
  const missionDescription = document.getElementById('missionDescription');
  const privacyNoticeText = document.getElementById('privacyNoticeText');
  const stepsList = document.getElementById('stepsList');
  const whatToBringText = document.getElementById('whatToBringText');
  const safetyNoteText = document.getElementById('safetyNoteText');
  const screenOffChallengeText = document.getElementById('screenOffChallengeText');

  const goOutsideBtn = document.getElementById('goOutsideBtn');
  const zenOverlay = document.getElementById('zenOverlay');
  const zenTimerDisplay = document.getElementById('zenTimerDisplay');
  const zenTimerPauseBtn = document.getElementById('zenTimerPauseBtn');
  const zenTimerResetBtn = document.getElementById('zenTimerResetBtn');
  const zenMissionTitle = document.getElementById('zenMissionTitle');
  const zenStepsContainer = document.getElementById('zenStepsContainer');
  const zenExitBtn = document.getElementById('zenExitBtn');

  // Form Fields
  const activityInput = document.getElementById('activityInput');
  const timeInput = document.getElementById('timeInput');
  const energyInput = document.getElementById('energyInput');
  const environmentInput = document.getElementById('environmentInput');
  const companyInput = document.getElementById('companyInput');
  const interestInput = document.getElementById('interestInput');
  const contextInput = document.getElementById('contextInput');

  // Presets definition
  const PRESETS = {
    campus: {
      activity: 'Nature exploration',
      time: '15 minutes',
      energy: 'Medium',
      environment: 'Campus',
      company: 'Solo',
      interest: 'Nature',
      context: 'College campus quad with mature trees and stone benches'
    },
    neighborhood: {
      activity: 'Walking',
      time: '30 minutes',
      energy: 'Medium',
      environment: 'Neighborhood',
      company: 'Solo',
      interest: 'Relaxation',
      context: 'Quiet residential street with sidewalks and garden yards'
    },
    photo: {
      activity: 'Photography',
      time: '45 minutes',
      energy: 'Medium',
      environment: 'Park',
      company: 'Solo',
      interest: 'Photography',
      context: 'City park with winding duck pond, shade trees, and flowerbeds'
    },
    friends: {
      activity: 'Nature exploration',
      time: '1 hour',
      energy: 'High',
      environment: 'Trail',
      company: 'With friends',
      interest: 'Exploration',
      context: 'Nature reserve walking trail with mild incline and woods'
    },
    gardening: {
      activity: 'Gardening',
      time: '30 minutes',
      energy: 'Low',
      environment: 'Garden',
      company: 'Solo',
      interest: 'Nature',
      context: 'Backyard garden beds and potted patio plants'
    }
  };

  // Rotating loading tips during local AI generation
  const LOADING_TIPS = [
    'Connecting to local open-weight model...',
    'Consulting local neural weights on your machine...',
    'Designing screen-free sensory milestones...',
    'Verifying outdoor safety and hydration guidance...',
    'Packaging your screen-off outdoor challenge...'
  ];
  let tipInterval = null;

  // Zen Mode Countdown State
  let currentMission = null;
  let timerInterval = null;
  let remainingSeconds = 30 * 60;
  let totalSeconds = 30 * 60;
  let isTimerPaused = false;

  // ==========================================================================
  // Ollama Status Check
  // ==========================================================================

  async function checkOllamaStatus() {
    statusDot.className = 'status-dot dot-checking';
    statusLabel.textContent = 'Checking Local AI...';

    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      if (data.online) {
        statusDot.className = 'status-dot dot-online';
        statusLabel.textContent = `Local AI: ${data.active_model} (Online)`;
        offlineBanner.classList.add('hidden');
      } else {
        statusDot.className = 'status-dot dot-offline';
        statusLabel.textContent = 'Local AI Offline';
        offlineBanner.classList.remove('hidden');
      }
    } catch (err) {
      console.warn('Status check failed:', err);
      statusDot.className = 'status-dot dot-offline';
      statusLabel.textContent = 'Local AI Offline';
      offlineBanner.classList.remove('hidden');
    }
  }

  refreshStatusBtn.addEventListener('click', checkOllamaStatus);

  // Copy command helper
  if (copyCmdBtn) {
    copyCmdBtn.addEventListener('click', () => {
      navigator.clipboard.writeText('ollama run qwen2.5:3b').then(() => {
        const orig = copyCmdBtn.textContent;
        copyCmdBtn.textContent = 'Copied!';
        setTimeout(() => {
          copyCmdBtn.textContent = orig;
        }, 2000);
      });
    });
  }

  // ==========================================================================
  // Presets Handlers
  // ==========================================================================

  document.querySelectorAll('.preset-pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const presetKey = btn.dataset.preset;
      const config = PRESETS[presetKey];
      if (!config) return;

      activityInput.value = config.activity;
      timeInput.value = config.time;
      energyInput.value = config.energy;
      environmentInput.value = config.environment;
      companyInput.value = config.company;
      interestInput.value = config.interest;
      contextInput.value = config.context;

      // Subtle visual pulse on the form
      const planner = document.getElementById('plannerSection');
      planner.style.borderColor = 'var(--forest-300)';
      setTimeout(() => {
        planner.style.borderColor = '';
      }, 500);

      // Scroll smoothly to form
      planner.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // ==========================================================================
  // Form Submission & Mission Generation
  // ==========================================================================

  missionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      activity: activityInput.value,
      time: timeInput.value,
      energy: energyInput.value,
      environment: environmentInput.value,
      company: companyInput.value,
      interest: interestInput.value,
      context: contextInput.value.trim()
    };

    // UI Loading state
    generateBtn.disabled = true;
    loadingState.classList.remove('hidden');

    let tipIndex = 0;
    loadingTip.textContent = LOADING_TIPS[0];
    tipInterval = setInterval(() => {
      tipIndex = (tipIndex + 1) % LOADING_TIPS.length;
      loadingTip.textContent = LOADING_TIPS[tipIndex];
    }, 2800);

    try {
      const response = await fetch('/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data && data.mission) {
        currentMission = data.mission;
        currentMission._meta = data;
        renderMission(data);
      } else {
        alert('Could not generate mission. Please try again.');
      }
    } catch (error) {
      console.error('Error generating mission:', error);
      alert('Network or server error while generating your mission. Please check the terminal.');
    } finally {
      clearInterval(tipInterval);
      loadingState.classList.add('hidden');
      generateBtn.disabled = false;
    }
  });

  // ==========================================================================
  // Render Mission Card UI
  // ==========================================================================

  function renderMission(data) {
    const mission = data.mission;
    const inputs = data.inputs || {};

    // Header Badges
    badgeDifficulty.textContent = mission.difficulty || 'Easy';
    badgeDuration.textContent = mission.estimated_duration || inputs.time || '30 minutes';
    badgeEnvironment.textContent = inputs.environment || 'Outdoors';

    if (data.source === 'local_ai') {
      badgeAiModel.textContent = `Local AI: ${data.model || 'Qwen 2.5 3B'}`;
      badgeAiModel.style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
      badgeAiModel.style.borderColor = 'rgba(16, 185, 129, 0.4)';
      badgeAiModel.style.color = '#6ee7b7';
      privacyNoticeText.textContent = 'Processed 100% locally on your machine with open-weight AI. Zero cloud trackers.';
    } else {
      badgeAiModel.textContent = 'Offline Fallback Planner';
      badgeAiModel.style.backgroundColor = 'rgba(245, 158, 11, 0.2)';
      badgeAiModel.style.borderColor = 'rgba(245, 158, 11, 0.4)';
      badgeAiModel.style.color = '#fde68a';
      privacyNoticeText.textContent = data.notice || 'Generated locally without cloud services.';
    }

    // Texts
    missionTitle.textContent = mission.mission_title || 'Your Outdoor Mission';
    missionDescription.textContent = mission.short_description || 'Step outside and reconnect with the world.';
    whatToBringText.textContent = mission.what_to_bring || 'Water bottle and comfortable shoes.';
    safetyNoteText.textContent = mission.safety_note || 'Stay aware of your surroundings.';
    screenOffChallengeText.textContent = mission.screen_off_challenge || 'Keep your phone locked in your pocket.';

    // Render Steps with Interactive Checkboxes
    stepsList.innerHTML = '';
    const rawSteps = Array.isArray(mission.steps) ? mission.steps : [];
    rawSteps.forEach((step, idx) => {
      const li = document.createElement('li');
      li.className = 'step-item';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.className = 'step-checkbox';
      checkbox.id = `step-check-${idx}`;

      const label = document.createElement('label');
      label.htmlFor = `step-check-${idx}`;
      label.className = 'step-text';
      label.textContent = step;

      checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
          li.classList.add('completed');
        } else {
          li.classList.remove('completed');
        }
      });

      li.appendChild(checkbox);
      li.appendChild(label);
      stepsList.appendChild(li);
    });

    // Populate Zen Steps Quick Glance as well
    zenMissionTitle.textContent = mission.mission_title || 'Your Outdoor Mission';
    zenStepsContainer.innerHTML = '';
    rawSteps.forEach(step => {
      const line = document.createElement('div');
      line.className = 'zen-step-line';
      line.textContent = step;
      zenStepsContainer.appendChild(line);
    });

    // Show Result Section & Smooth Scroll
    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ==========================================================================
  // Zen Mode "GO OUTSIDE 🌱"
  // ==========================================================================

  function parseDurationToSeconds(durationStr) {
    if (!durationStr) return 30 * 60;
    const lower = String(durationStr).toLowerCase();

    if (lower.includes('15') && lower.includes('min')) return 15 * 60;
    if (lower.includes('30') && lower.includes('min')) return 30 * 60;
    if (lower.includes('45') && lower.includes('min')) return 45 * 60;
    if (lower.includes('1') && lower.includes('hour')) return 60 * 60;
    if (lower.includes('2') && lower.includes('hour')) return 120 * 60;

    // Check for any number of minutes
    const matchMin = lower.match(/(\d+)\s*m/);
    if (matchMin) return parseInt(matchMin[1], 10) * 60;

    const matchHour = lower.match(/(\d+)\s*h/);
    if (matchHour) return parseInt(matchHour[1], 10) * 3600;

    return 30 * 60;
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  function startZenTimer(initialSeconds) {
    clearInterval(timerInterval);
    remainingSeconds = initialSeconds;
    totalSeconds = initialSeconds;
    isTimerPaused = false;
    zenTimerPauseBtn.textContent = 'Pause';

    zenTimerDisplay.textContent = formatTime(remainingSeconds);

    timerInterval = setInterval(() => {
      if (!isTimerPaused) {
        remainingSeconds--;
        if (remainingSeconds <= 0) {
          clearInterval(timerInterval);
          zenTimerDisplay.textContent = "00:00";
          zenTimerPauseBtn.disabled = true;
          alert('🌿 Mission Complete! Welcome back from touching grass!');
        } else {
          zenTimerDisplay.textContent = formatTime(remainingSeconds);
        }
      }
    }, 1000);
  }

  goOutsideBtn.addEventListener('click', () => {
    const durationStr = (currentMission && currentMission.estimated_duration)
      ? currentMission.estimated_duration
      : timeInput.value;

    const seconds = parseDurationToSeconds(durationStr);
    startZenTimer(seconds);

    zenOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  });

  zenTimerPauseBtn.addEventListener('click', () => {
    isTimerPaused = !isTimerPaused;
    zenTimerPauseBtn.textContent = isTimerPaused ? 'Resume' : 'Pause';
  });

  zenTimerResetBtn.addEventListener('click', () => {
    startZenTimer(totalSeconds);
  });

  zenExitBtn.addEventListener('click', () => {
    clearInterval(timerInterval);
    zenOverlay.classList.add('hidden');
    document.body.style.overflow = '';
  });

  // Initial check on load
  checkOllamaStatus();
});
