// script.js - Saarthi on iQOO Devices: Interactive Prototype & Sensor Fusion Controller

document.addEventListener('DOMContentLoaded', () => {
  const audio = window.sarthiAudio;
  let voiceoverEnabled = true;

  // Tab Navigation
  const tabBtns = document.querySelectorAll('.nav-tab-btn');
  const tabSections = document.querySelectorAll('.tab-section');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      tabSections.forEach(s => s.classList.remove('active'));

      btn.classList.add('active');
      const targetSection = document.getElementById(targetTab);
      if (targetSection) targetSection.classList.add('active');
    });
  });

  // =========================================================================
  // iQOO LIVE PROTOTYPE ENGINE
  // =========================================================================
  const scenarioData = {
    auto_rickshaw: {
      state: 'HAZARD',
      class: 'verdict-hazard',
      icon: '🚨',
      distance: 'DIST 2.1m',
      spoken: 'Hazard in path. Auto-rickshaw turning 2.1 meters ahead. Step left onto curb.',
      box1: { tag: 'VEHICLE // 2.1m [98%]', type: 'box-alert', top: '30%', left: '24%', width: '140px', height: '160px' },
      box2: { tag: 'CURB // 0.8m [94%]', type: 'box-caution', bottom: '22%', right: '18%', width: '90px', height: '50px' },
      checks: [
        { name: '1. Object Taxonomy', desc: 'Vehicle / Rickshaw detected', status: 'MATCH (0.98)', type: 'alert' },
        { name: '2. Distance vs Threshold', desc: '2.1m < safe-stop (2.5m)', status: 'CRITICAL', type: 'alert' },
        { name: '3. Motion Trajectory', desc: 'Velocity vector closing in', status: 'CLOSING IN', type: 'alert' },
        { name: '4. Path Relevance', desc: 'Inside walking corridor', status: 'IN CORRIDOR', type: 'warn' },
        { name: '5. Temporal Persistence', desc: 'Held across 5+ frames', status: 'VERIFIED (5F)', type: 'passed' },
        { name: '6. Ambient Context', desc: 'Dusk lighting + traffic noise', status: 'BOOST GAIN', type: 'passed' }
      ]
    },
    pedestrian_crowd: {
      state: 'CAUTION',
      class: 'verdict-caution',
      icon: '⚠️',
      distance: 'DIST 1.4m',
      spoken: 'Caution. Pedestrian crossing walking corridor at 1.4 meters.',
      box1: { tag: 'PEDESTRIAN // 1.4m [96%]', type: 'box-caution', top: '24%', left: '35%', width: '100px', height: '180px' },
      box2: { tag: 'CHAI STALL // 3.2m', type: 'box-safe', top: '20%', right: '10%', width: '80px', height: '100px' },
      checks: [
        { name: '1. Object Taxonomy', desc: 'Pedestrian detected', status: 'MATCH (0.96)', type: 'warn' },
        { name: '2. Distance vs Threshold', desc: '1.4m (Caution zone)', status: 'MONITOR', type: 'warn' },
        { name: '3. Motion Trajectory', desc: 'Lateral crossing vector', status: 'CROSSING', type: 'warn' },
        { name: '4. Path Relevance', desc: 'Edge of walking corridor', status: 'CORRIDOR EDGE', type: 'warn' },
        { name: '5. Temporal Persistence', desc: 'Held across 6 frames', status: 'VERIFIED (6F)', type: 'passed' },
        { name: '6. Ambient Context', desc: 'Normal daylight audio', status: 'NORMAL GAIN', type: 'passed' }
      ]
    },
    curb_pothole: {
      state: 'CAUTION',
      class: 'verdict-caution',
      icon: '⚠️',
      distance: 'DIST 0.8m',
      spoken: 'Caution. Uneven sidewalk curb drop in two paces. Step down carefully.',
      box1: { tag: 'CURB DROP // 0.8m [97%]', type: 'box-caution', bottom: '20%', left: '25%', width: '160px', height: '60px' },
      box2: { tag: 'PAVEMENT // SAFE', type: 'box-safe', top: '40%', left: '15%', width: '80px', height: '60px' },
      checks: [
        { name: '1. Object Taxonomy', desc: 'Tactile curb / Step down', status: 'MATCH (0.97)', type: 'warn' },
        { name: '2. Distance vs Threshold', desc: '0.8m (Imminent step)', status: 'ALERT STEP', type: 'alert' },
        { name: '3. Motion Trajectory', desc: 'Stationary physical structure', status: 'STATIC', type: 'passed' },
        { name: '4. Path Relevance', desc: 'Directly in path line', status: 'CENTER PATH', type: 'alert' },
        { name: '5. Temporal Persistence', desc: 'Continuous elevation edge', status: 'CONFIRMED', type: 'passed' },
        { name: '6. Ambient Context', desc: 'Shadowed pavement', status: 'ENHANCE CONTRAST', type: 'passed' }
      ]
    },
    clear_path: {
      state: 'CLEAR',
      class: 'verdict-clear',
      icon: '✅',
      distance: 'DIST >4.5m',
      spoken: 'Path clear for four meters. Walkable corridor confirmed.',
      box1: { tag: 'CLEAR CORRIDOR [99%]', type: 'box-safe', top: '25%', left: '20%', width: '180px', height: '220px' },
      box2: { tag: 'HORIZON OPEN', type: 'box-safe', top: '15%', right: '20%', width: '70px', height: '40px' },
      checks: [
        { name: '1. Object Taxonomy', desc: 'No hazardous obstacle in taxonomy', status: 'CLEAR (0.99)', type: 'passed' },
        { name: '2. Distance vs Threshold', desc: 'Obstacle distance > 4.5m', status: 'SAFE RANGE', type: 'passed' },
        { name: '3. Motion Trajectory', desc: 'No closing vectors', status: 'ZERO THREAT', type: 'passed' },
        { name: '4. Path Relevance', desc: 'Walking corridor open', status: 'FREE PATH', type: 'passed' },
        { name: '5. Temporal Persistence', desc: 'Continuous clear state (12F)', status: 'PERSISTED', type: 'passed' },
        { name: '6. Ambient Context', desc: 'Optimal lighting condition', status: 'CALIBRATED', type: 'passed' }
      ]
    }
  };

  const scenarioCards = document.querySelectorAll('.scenario-card');
  const hudVerdictBanner = document.getElementById('hudVerdictBanner');
  const verdictIcon = document.getElementById('verdictIcon');
  const verdictStateTitle = document.getElementById('verdictStateTitle');
  const verdictDistance = document.getElementById('verdictDistance');
  const hudSpokenText = document.getElementById('hudSpokenText');
  const protoBox1 = document.getElementById('protoBox1');
  const protoBoxTag1 = document.getElementById('protoBoxTag1');
  const protoBox2 = document.getElementById('protoBox2');
  const protoBoxTag2 = document.getElementById('protoBoxTag2');
  const checksMatrixList = document.getElementById('checksMatrixList');
  const narrationToggleBtn = document.getElementById('narrationToggleBtn');
  const contrastToggleBtn = document.getElementById('contrastToggleBtn');

  function speakNarration(text) {
    if (!voiceoverEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    audio.duckAudio(true);

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.02;

    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('en-GB') || v.lang.includes('en-US'));
    if (englishVoice) utterance.voice = englishVoice;

    utterance.onend = () => audio.duckAudio(false);
    utterance.onerror = () => audio.duckAudio(false);
    window.speechSynthesis.speak(utterance);
  }

  function applyScenario(scKey) {
    const sc = scenarioData[scKey];
    if (!sc) return;

    // Update Verdict Banner
    hudVerdictBanner.className = `hud-verdict-banner ${sc.class}`;
    verdictIcon.textContent = sc.icon;
    verdictStateTitle.textContent = sc.state;
    verdictDistance.textContent = sc.distance;
    hudSpokenText.textContent = `"${sc.spoken}"`;

    // Update Bounding Boxes
    protoBox1.className = `bounding-box ${sc.box1.type} active`;
    protoBoxTag1.textContent = sc.box1.tag;
    protoBox1.style.top = sc.box1.top || 'auto';
    protoBox1.style.bottom = sc.box1.bottom || 'auto';
    protoBox1.style.left = sc.box1.left || 'auto';
    protoBox1.style.right = sc.box1.right || 'auto';
    protoBox1.style.width = sc.box1.width;
    protoBox1.style.height = sc.box1.height;

    protoBox2.className = `bounding-box ${sc.box2.type} active`;
    protoBoxTag2.textContent = sc.box2.tag;
    protoBox2.style.top = sc.box2.top || 'auto';
    protoBox2.style.bottom = sc.box2.bottom || 'auto';
    protoBox2.style.left = sc.box2.left || 'auto';
    protoBox2.style.right = sc.box2.right || 'auto';
    protoBox2.style.width = sc.box2.width;
    protoBox2.style.height = sc.box2.height;

    // Update 6 Sensing Checks Matrix
    checksMatrixList.innerHTML = sc.checks.map(c => `
      <div class="check-item-card ${c.type}">
        <div>
          <div class="check-title">${c.name}</div>
          <span style="font-size: 0.7rem; color: var(--text-muted);">${c.desc}</span>
        </div>
        <span class="check-status" style="color: ${c.type === 'alert' ? 'var(--accent-red)' : c.type === 'warn' ? 'var(--accent-amber)' : 'var(--accent-green)'};">${c.status}</span>
      </div>
    `).join('');

    // Audio Feedback
    if (sc.state === 'HAZARD') {
      audio.playRadarPing(true);
    } else if (sc.state === 'CAUTION') {
      audio.playRadarPing(false);
    } else {
      audio.playNavigationChime();
    }

    speakNarration(sc.spoken);
  }

  scenarioCards.forEach(card => {
    card.addEventListener('click', () => {
      scenarioCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      applyScenario(card.dataset.scenario);
    });
  });

  // Hotword Wake Button
  document.getElementById('btnVoiceWakeHotword')?.addEventListener('click', () => {
    audio.playVoiceWakeSound();
    speakNarration('Saarthi listening. How can I guide you?');
  });

  // Controls
  narrationToggleBtn?.addEventListener('click', () => {
    voiceoverEnabled = !voiceoverEnabled;
    narrationToggleBtn.classList.toggle('active', voiceoverEnabled);
    narrationToggleBtn.querySelector('span').textContent = voiceoverEnabled ? 'Audio TTS: ON' : 'Audio TTS: OFF';
    if (!voiceoverEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  });

  contrastToggleBtn?.addEventListener('click', () => {
    document.body.classList.toggle('high-contrast');
    contrastToggleBtn.classList.toggle('active', document.body.classList.contains('high-contrast'));
  });

  // Initial Scenario
  applyScenario('auto_rickshaw');
});
