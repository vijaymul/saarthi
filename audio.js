// audio.js - Web Audio API Procedural Sound Engine & Audio Ducking System for Sarthi Demo

class SarthiAudioEngine {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.bgmVolume = 0.35;
    this.sfxVolume = 0.6;
    this.isPlayingBgm = false;
    this.duckingTarget = 0.35;
    this.currentGainNode = null;
    this.ambientOscillators = [];
    this.musicTimer = null;
    this.beatIndex = 0;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  startBGM(intensity = 'ambient') {
    this.init();
    if (this.isPlayingBgm) return;
    this.isPlayingBgm = true;

    this.masterBgmGain = this.ctx.createGain();
    this.masterBgmGain.gain.setValueAtTime(this.isMuted ? 0 : this.bgmVolume, this.ctx.currentTime);
    this.masterBgmGain.connect(this.ctx.destination);

    const chords = [
      [174.61, 220.00, 261.63, 349.23],
      [207.65, 261.63, 311.13, 415.30],
      [155.56, 196.00, 233.08, 311.13],
      [233.08, 293.66, 349.23, 466.16]
    ];

    let chordIdx = 0;
    const playChord = () => {
      if (!this.isPlayingBgm) return;
      const currentChord = chords[chordIdx % chords.length];
      chordIdx++;

      currentChord.forEach((freq, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const filter = this.ctx.createBiquadFilter();

        osc.type = i === 0 ? 'triangle' : 'sine';
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(650 + (i * 200), this.ctx.currentTime);

        const now = this.ctx.currentTime;
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.045 / (i + 1), now + 1.2);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 4.8);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterBgmGain);

        osc.start(now);
        osc.stop(now + 5.0);
      });

      this.musicTimer = setTimeout(playChord, 4500);
    };

    playChord();
  }

  stopBGM() {
    this.isPlayingBgm = false;
    if (this.musicTimer) clearTimeout(this.musicTimer);
    if (this.masterBgmGain && this.ctx) {
      this.masterBgmGain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.5);
    }
  }

  duckAudio(isDucking) {
    if (!this.masterBgmGain || !this.ctx || this.isMuted) return;
    const now = this.ctx.currentTime;
    const targetVolume = isDucking ? this.bgmVolume * 0.22 : this.bgmVolume;
    this.masterBgmGain.gain.cancelScheduledValues(now);
    this.masterBgmGain.gain.linearRampToValueAtTime(targetVolume, now + 0.35);
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.masterBgmGain && this.ctx) {
      const now = this.ctx.currentTime;
      this.masterBgmGain.gain.linearRampToValueAtTime(this.isMuted ? 0 : this.bgmVolume, now + 0.1);
    }
    return this.isMuted;
  }

  playVoiceWakeSound() {
    if (this.isMuted) return;
    this.init();
    const freqs = [440, 659.25, 880, 1318.5];
    freqs.forEach((f, idx) => {
      setTimeout(() => {
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, this.ctx.currentTime);

          const now = this.ctx.currentTime;
          gain.gain.setValueAtTime(0.001, now);
          gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.18, now + 0.04);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);

          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + 0.5);
        } catch (e) {}
      }, idx * 70);
    });
  }

  playRadarPing(isAlert = false) {
    if (this.isMuted) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = isAlert ? 'sawtooth' : 'triangle';
      osc.frequency.setValueAtTime(isAlert ? 880 : 587.33, this.ctx.currentTime);
      if (isAlert) {
        osc.frequency.exponentialRampToValueAtTime(440, this.ctx.currentTime + 0.2);
      }

      const now = this.ctx.currentTime;
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.15, now + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + (isAlert ? 0.3 : 0.22));

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.35);
    } catch (e) {}
  }

  playNavigationChime() {
    if (this.isMuted) return;
    this.init();
    const chords = [523.25, 659.25, 783.99];
    chords.forEach((f, idx) => {
      setTimeout(() => {
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, this.ctx.currentTime);

          const now = this.ctx.currentTime;
          gain.gain.setValueAtTime(0.001, now);
          gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.14, now + 0.05);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.6);

          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + 0.65);
        } catch (e) {}
      }, idx * 80);
    });
  }

  playSOSPulseSound() {
    if (this.isMuted) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(329.63, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(659.25, this.ctx.currentTime + 0.25);

      const now = this.ctx.currentTime;
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.22, now + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.7);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.75);
    } catch (e) {}
  }

  playTerminalKeypress() {
    if (this.isMuted) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(1200 + Math.random() * 400, this.ctx.currentTime);

      const now = this.ctx.currentTime;
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(this.sfxVolume * 0.025, now + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.04);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.05);
    } catch (e) {}
  }
}

window.sarthiAudio = new SarthiAudioEngine();
