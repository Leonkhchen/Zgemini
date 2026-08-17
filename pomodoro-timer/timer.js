/**
 * AuraFocus Pomodoro Timer Engine
 */
export class Timer {
  constructor(soundboard, onSessionComplete) {
    this.soundboard = soundboard;
    this.onSessionComplete = onSessionComplete; // callback to sync task/stat updates
    
    // Default Settings
    this.durations = {
      pomodoro: 25 * 60, // in seconds
      'short-break': 5 * 60,
      'long-break': 15 * 60
    };
    
    this.settings = {
      chimeVolume: 0.5,
      dailyGoal: 4,
      autoBreaks: false,
      autoPomodoros: false
    };

    // Timer State
    this.mode = 'pomodoro'; // 'pomodoro' | 'short-break' | 'long-break'
    this.state = 'idle'; // 'idle' | 'running' | 'paused'
    this.timeLeft = this.durations.pomodoro;
    this.totalDuration = this.durations.pomodoro;
    this.intervalId = null;

    // Daily Stats (persist in localStorage)
    this.stats = {
      completedToday: 0,
      totalMinutesToday: 0,
      date: new Date().toDateString()
    };

    this.loadSettingsAndStats();
    this.initDOM();
    this.updateUI();
  }

  initDOM() {
    this.countdownEl = document.getElementById('timer-countdown');
    this.stateLabelEl = document.getElementById('timer-state-label');
    this.progressRing = document.getElementById('timer-progress-ring');
    this.goalRing = document.getElementById('goal-progress-ring');
    this.goalText = document.getElementById('goal-percentage');
    this.quickCountText = document.getElementById('quick-count');
    this.statTimeText = document.getElementById('stat-total-time');
    this.statSessionsText = document.getElementById('stat-sessions');

    // Controls
    this.playPauseBtn = document.getElementById('play-pause-btn');
    this.playIcon = this.playPauseBtn.querySelector('.play-icon');
    this.pauseIcon = this.playPauseBtn.querySelector('.pause-icon');
    this.resetBtn = document.getElementById('reset-btn');
    this.skipBtn = document.getElementById('skip-btn');

    // Mode Buttons
    this.modeBtns = document.querySelectorAll('.mode-btn');

    this.initEventListeners();
  }

  initEventListeners() {
    this.playPauseBtn.addEventListener('click', () => this.toggle());
    this.resetBtn.addEventListener('click', () => this.reset());
    this.skipBtn.addEventListener('click', () => this.skip());

    this.modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-mode');
        this.switchMode(mode);
      });
    });
  }

  loadSettingsAndStats() {
    // Load Durations & Settings
    const savedDurations = localStorage.getItem('aurafocus-durations');
    if (savedDurations) {
      const parsed = JSON.parse(savedDurations);
      this.durations.pomodoro = parsed.pomodoro * 60;
      this.durations['short-break'] = parsed['short-break'] * 60;
      this.durations['long-break'] = parsed['long-break'] * 60;
    }

    const savedSettings = localStorage.getItem('aurafocus-settings');
    if (savedSettings) {
      this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
    }

    // Load/Reset stats per day
    const savedStats = localStorage.getItem('aurafocus-stats');
    if (savedStats) {
      const parsed = JSON.parse(savedStats);
      if (parsed.date === new Date().toDateString()) {
        this.stats = parsed;
      } else {
        // New day reset
        this.stats.date = new Date().toDateString();
        this.saveStats();
      }
    }

    this.timeLeft = this.durations[this.mode];
    this.totalDuration = this.durations[this.mode];
  }

  saveSettings() {
    localStorage.setItem('aurafocus-durations', JSON.stringify({
      pomodoro: this.durations.pomodoro / 60,
      'short-break': this.durations['short-break'] / 60,
      'long-break': this.durations['long-break'] / 60
    }));

    localStorage.setItem('aurafocus-settings', JSON.stringify(this.settings));
    this.updateUI();
  }

  saveStats() {
    localStorage.setItem('aurafocus-stats', JSON.stringify(this.stats));
  }

  updateUI() {
    // Update Timer Text
    const min = Math.floor(this.timeLeft / 60);
    const sec = this.timeLeft % 60;
    const padMin = String(min).padStart(2, '0');
    const padSec = String(sec).padStart(2, '0');
    const timerStr = `${padMin}:${padSec}`;
    
    this.countdownEl.textContent = timerStr;
    
    // Page Title Update
    const modeLabel = this.mode === 'pomodoro' ? 'Focus' : 'Break';
    document.title = `${timerStr} — ${modeLabel} | AuraFocus`;

    // State labels
    if (this.state === 'running') {
      this.stateLabelEl.textContent = this.mode === 'pomodoro' ? 'Deep Focus' : 'Relaxing Break';
      this.playIcon.classList.add('hidden');
      this.pauseIcon.classList.remove('hidden');
    } else if (this.state === 'paused') {
      this.stateLabelEl.textContent = 'Paused';
      this.playIcon.classList.remove('hidden');
      this.pauseIcon.classList.add('hidden');
    } else {
      this.stateLabelEl.textContent = 'Ready to Focus';
      this.playIcon.classList.remove('hidden');
      this.pauseIcon.classList.add('hidden');
    }

    // Circular Timer Progress Ring
    const timerCircumference = 552.92; // 2 * pi * 88
    const progress = this.timeLeft / this.totalDuration;
    const offset = timerCircumference * (1 - progress);
    this.progressRing.style.strokeDashoffset = offset;

    // Mode Buttons active sync
    this.modeBtns.forEach(btn => {
      if (btn.getAttribute('data-mode') === this.mode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update Stats Display
    this.statSessionsText.textContent = this.stats.completedToday;
    this.statTimeText.textContent = `${this.stats.totalMinutesToday}m`;
    this.quickCountText.textContent = `${this.stats.completedToday}/${this.settings.dailyGoal} Pomodoros`;

    // Daily Goal progress ring
    const goalCircumference = 263.89; // 2 * pi * 42
    const target = this.settings.dailyGoal;
    const percentage = Math.min(Math.round((this.stats.completedToday / target) * 100), 100);
    this.goalText.textContent = `${percentage}%`;

    const goalProgress = this.stats.completedToday / target;
    const goalOffset = goalCircumference * (1 - Math.min(goalProgress, 1));
    this.goalRing.style.strokeDashoffset = goalOffset;
  }

  toggle() {
    if (this.state === 'running') {
      this.pause();
    } else {
      this.start();
    }
  }

  start() {
    if (this.state === 'running') return;
    
    // Resume Audio Context in Soundboard if it was suspended
    if (this.soundboard) {
      this.soundboard.initAudioContext();
    }

    this.state = 'running';
    this.updateUI();

    this.intervalId = setInterval(() => {
      this.timeLeft--;
      
      if (this.timeLeft <= 0) {
        this.sessionCompleted();
      } else {
        this.updateUI();
      }
    }, 1000);
  }

  pause() {
    if (this.state !== 'running') return;
    this.state = 'paused';
    clearInterval(this.intervalId);
    this.intervalId = null;
    this.updateUI();
  }

  reset() {
    this.pause();
    this.state = 'idle';
    this.timeLeft = this.durations[this.mode];
    this.totalDuration = this.durations[this.mode];
    this.updateUI();
  }

  skip() {
    this.pause();
    // Prompt chime, transition to next mode
    this.soundboard.playChime(this.settings.chimeVolume);
    this.transitionNextMode();
  }

  switchMode(newMode) {
    this.pause();
    this.mode = newMode;
    this.state = 'idle';
    this.timeLeft = this.durations[this.mode];
    this.totalDuration = this.durations[this.mode];
    this.updateUI();
  }

  sessionCompleted() {
    this.pause();
    
    // Play physical sound notification
    this.soundboard.playChime(this.settings.chimeVolume);

    if (this.mode === 'pomodoro') {
      // Completed Pomodoro session
      this.stats.completedToday++;
      // Increment focus duration
      const focusMin = Math.round(this.durations.pomodoro / 60);
      this.stats.totalMinutesToday += focusMin;
      this.saveStats();

      // Trigger task progress update in app.js callback
      if (this.onSessionComplete) {
        this.onSessionComplete('pomodoro');
      }
    } else {
      // Finished break
      if (this.onSessionComplete) {
        this.onSessionComplete('break');
      }
    }

    this.transitionNextMode();
  }

  transitionNextMode() {
    if (this.mode === 'pomodoro') {
      // Determine break: if completed 4th (or multiple of 4) pomodoro, take long break
      const isLongBreak = this.stats.completedToday > 0 && this.stats.completedToday % 4 === 0;
      this.mode = isLongBreak ? 'long-break' : 'short-break';
      this.timeLeft = this.durations[this.mode];
      this.totalDuration = this.durations[this.mode];
      this.state = 'idle';

      if (this.settings.autoBreaks) {
        this.start();
      } else {
        this.updateUI();
      }
    } else {
      // Transition from break to pomodoro focus
      this.mode = 'pomodoro';
      this.timeLeft = this.durations[this.mode];
      this.totalDuration = this.durations[this.mode];
      this.state = 'idle';

      if (this.settings.autoPomodoros) {
        this.start();
      } else {
        this.updateUI();
      }
    }
  }

  // Update configurations from settings panel
  updateSettings(durationsConfig, generalSettings) {
    this.durations.pomodoro = durationsConfig.pomodoro * 60;
    this.durations['short-break'] = durationsConfig.shortBreak * 60;
    this.durations['long-break'] = durationsConfig.longBreak * 60;

    this.settings.chimeVolume = generalSettings.chimeVolume;
    this.settings.dailyGoal = generalSettings.dailyGoal;
    this.settings.autoBreaks = generalSettings.autoBreaks;
    this.settings.autoPomodoros = generalSettings.autoPomodoros;

    this.saveSettings();
    this.reset(); // reset to reflect new times
  }
}
