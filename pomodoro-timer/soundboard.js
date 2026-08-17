/**
 * AuraFocus Ambient Sound Synthesis Engine using Web Audio API
 */
export class Soundboard {
  constructor() {
    this.audioCtx = null;
    this.sounds = {
      rain: { playing: false, volume: 0.4, source: null, gainNode: null, filterNode: null },
      waves: { playing: false, volume: 0.3, source: null, gainNode: null, lfo: null, filterNode: null },
      white: { playing: false, volume: 0.2, source: null, gainNode: null, filterNode: null }
    };
    
    this.enableBtn = document.getElementById('enable-audio-btn');
    this.initEventListeners();
    this.checkAudioState();
  }

  initEventListeners() {
    // Sound toggles
    document.querySelectorAll('.sound-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const soundType = btn.getAttribute('data-sound');
        this.toggleSound(soundType);
      });
    });

    // Volume sliders
    document.querySelectorAll('.volume-slider').forEach(slider => {
      slider.addEventListener('input', (e) => {
        const soundType = e.target.getAttribute('data-sound');
        const volumeVal = parseFloat(e.target.value) / 100;
        this.setVolume(soundType, volumeVal);
      });
    });

    // Enable audio overlay button
    if (this.enableBtn) {
      this.enableBtn.addEventListener('click', () => {
        this.initAudioContext();
      });
    }

    // Proactively try to resume on general document click
    const resumeOnInteraction = () => {
      if (this.audioCtx && this.audioCtx.state === 'suspended') {
        this.audioCtx.resume().then(() => this.checkAudioState());
      }
    };
    document.body.addEventListener('click', resumeOnInteraction, { once: false });
  }

  checkAudioState() {
    if (!this.audioCtx) {
      this.enableBtn.classList.remove('hidden');
      return;
    }

    if (this.audioCtx.state === 'suspended') {
      this.enableBtn.classList.remove('hidden');
    } else {
      this.enableBtn.classList.add('hidden');
    }
  }

  async initAudioContext() {
    if (this.audioCtx) {
      if (this.audioCtx.state === 'suspended') {
        await this.audioCtx.resume();
      }
      this.checkAudioState();
      return;
    }

    try {
      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      this.checkAudioState();
    } catch (e) {
      console.error('Web Audio API not supported in this browser.', e);
    }
  }

  // --- Noise Buffer Generators ---
  
  // Pink Noise for Rain and Waves
  createPinkNoiseBuffer() {
    const bufferSize = 2 * this.audioCtx.sampleRate;
    const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
    const data = buffer.getChannelData(0);
    
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      data[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
      data[i] *= 0.11; // scaling compensation
      b6 = white * 0.115926;
    }
    return buffer;
  }

  // Brown Noise for Focus (deep water fall sound)
  createBrownNoiseBuffer() {
    const bufferSize = 2 * this.audioCtx.sampleRate;
    const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
    const data = buffer.getChannelData(0);
    
    let lastOut = 0.0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      data[i] = (lastOut + (0.02 * white)) / 1.02;
      lastOut = data[i];
      data[i] *= 3.5; // volume compensation
    }
    return buffer;
  }

  async toggleSound(soundType) {
    await this.initAudioContext();
    if (!this.audioCtx) return;

    const sound = this.sounds[soundType];
    const btn = document.querySelector(`.sound-toggle-btn[data-sound="${soundType}"]`);

    if (sound.playing) {
      // Pause
      this.stopSynthesizer(soundType);
      btn.classList.remove('active');
    } else {
      // Play
      this.startSynthesizer(soundType);
      btn.classList.add('active');
    }
  }

  startSynthesizer(soundType) {
    const sound = this.sounds[soundType];
    if (sound.playing) return;

    // Create noise source
    sound.source = this.audioCtx.createBufferSource();
    
    // Choose noise type
    if (soundType === 'rain' || soundType === 'waves') {
      sound.source.buffer = this.createPinkNoiseBuffer();
    } else if (soundType === 'white') {
      sound.source.buffer = this.createBrownNoiseBuffer();
    }
    sound.source.loop = true;

    // Create Gain Node
    sound.gainNode = this.audioCtx.createGain();
    
    // Set sound-specific volume scaling
    if (soundType === 'waves') {
      // Waves will have volume modulated by LFO
      sound.gainNode.gain.value = 0.1; // Base volume
    } else {
      sound.gainNode.gain.value = sound.volume;
    }

    // Create filters for calm timber
    sound.filterNode = this.audioCtx.createBiquadFilter();
    if (soundType === 'rain') {
      sound.filterNode.type = 'lowpass';
      sound.filterNode.frequency.value = 1400; // crispy rain, remove high scratchiness
      
      const highpass = this.audioCtx.createBiquadFilter();
      highpass.type = 'highpass';
      highpass.frequency.value = 150; // remove mud
      
      sound.source.connect(highpass);
      highpass.connect(sound.filterNode);
    } else if (soundType === 'waves') {
      sound.filterNode.type = 'lowpass';
      sound.filterNode.frequency.value = 400; // low wave rumble
      sound.source.connect(sound.filterNode);
    } else if (soundType === 'white') {
      sound.filterNode.type = 'lowpass';
      sound.filterNode.frequency.value = 1000; // soft warm waterfall focus
      sound.source.connect(sound.filterNode);
    }

    // Hook up LFO for Ocean Waves
    if (soundType === 'waves') {
      // Create LFO
      sound.lfo = this.audioCtx.createOscillator();
      sound.lfo.frequency.value = 0.08; // ~12.5 seconds wave period
      
      const lfoGain = this.audioCtx.createGain();
      // Wave volume swings up and down by this amount
      lfoGain.gain.value = sound.volume * 0.7; 
      
      // Offset base level
      sound.gainNode.gain.value = sound.volume * 0.3;

      // Connect LFO -> LFO Gain -> Destination Gain Node parameter
      sound.lfo.connect(lfoGain);
      lfoGain.connect(sound.gainNode.gain);
      
      // Connect sound path
      sound.filterNode.connect(sound.gainNode);
      sound.gainNode.connect(this.audioCtx.destination);

      // Start LFO
      sound.lfo.start(0);
    } else {
      // Direct sound path connection
      sound.filterNode.connect(sound.gainNode);
      sound.gainNode.connect(this.audioCtx.destination);
    }

    // Start playing noise
    sound.source.start(0);
    sound.playing = true;
  }

  stopSynthesizer(soundType) {
    const sound = this.sounds[soundType];
    if (!sound.playing) return;

    try {
      if (sound.source) {
        sound.source.stop(0);
        sound.source.disconnect();
      }
      if (sound.lfo) {
        sound.lfo.stop(0);
        sound.lfo.disconnect();
      }
      if (sound.gainNode) {
        sound.gainNode.disconnect();
      }
      if (sound.filterNode) {
        sound.filterNode.disconnect();
      }
    } catch (e) {
      console.warn('Error while stopping synthesizer nodes', e);
    }

    sound.source = null;
    sound.gainNode = null;
    sound.filterNode = null;
    sound.lfo = null;
    sound.playing = false;
  }

  setVolume(soundType, val) {
    const sound = this.sounds[soundType];
    sound.volume = val;

    if (sound.playing && sound.gainNode) {
      if (soundType === 'waves') {
        // Stop current nodes and restart so LFO scaling adjusts to the new volume setting.
        // Doing it instantly requires shifting nodes, but simple restart is clean or we can modulate lfoGain.
        // Let's do a simple volume adjustment.
        // If we want immediate feedback, we can stop and start, but just scaling base volume is fine.
        this.stopSynthesizer(soundType);
        this.startSynthesizer(soundType);
      } else {
        // Smooth transition to avoid pops
        sound.gainNode.gain.setTargetAtTime(val, this.audioCtx.currentTime, 0.05);
      }
    }
  }

  // Helper function to synthesize a warm, resonant focus chime.
  // Can be called by the timer when a session is complete.
  playChime(volume = 0.5) {
    if (!this.audioCtx) {
      this.initAudioContext();
      if (!this.audioCtx) return;
    }

    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }

    const t = this.audioCtx.currentTime;
    
    // Aesthetic chime is a blend of a main warm sine wave oscillator and a subtle third-harmonic oscillator
    const osc1 = this.audioCtx.createOscillator();
    const osc2 = this.audioCtx.createOscillator();
    const gainNode = this.audioCtx.createGain();

    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(523.25, t); // C5 - Clear chime tone
    
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(1046.50, t); // C6 - Sparkly octave harmonic

    // Set gain envelope for calming fade
    gainNode.gain.setValueAtTime(0, t);
    // Smooth attack to make it gentle, not a click
    gainNode.gain.linearRampToValueAtTime(volume * 0.7, t + 0.08); 
    // Exponential decay (long ringout)
    gainNode.gain.setTargetAtTime(0, t + 0.1, 0.8);

    osc1.connect(gainNode);
    osc2.connect(gainNode);
    
    // Add a simple bandpass filter to warm up the sound
    const filter = this.audioCtx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(600, t);
    filter.Q.setValueAtTime(1.0, t);

    gainNode.connect(filter);
    filter.connect(this.audioCtx.destination);

    osc1.start(t);
    osc2.start(t);

    // Stop nodes after chime is finished ringing out
    osc1.stop(t + 4.5);
    osc2.stop(t + 4.5);
  }
}
