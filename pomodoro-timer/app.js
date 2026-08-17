/**
 * AuraFocus Application Orchestrator
 */
import { initTheme } from './theme.js';
import { Soundboard } from './soundboard.js';
import { Timer } from './timer.js';
import { TaskManager } from './tasks.js';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Theme Engine
  initTheme();

  // 2. Initialize Ambient Audio Engine
  const soundboard = new Soundboard();

  // 3. Initialize Task Manager
  // Pass a callback to run when the active task is updated (optional, for custom syncing)
  const taskManager = new TaskManager((focusedTask) => {
    // If we want to perform any app-wide action when the focused task changes, do it here.
    // (e.g., logging or changing background glow intensity)
  });

  // 4. Initialize Timer Engine
  // Pass a callback to trigger when a Pomodoro session completes
  const timer = new Timer(soundboard, (sessionType) => {
    if (sessionType === 'pomodoro') {
      // Increment the pomodoro count on the active focused task
      taskManager.incrementCompletedPomodoro();
    }
  });

  // 5. Connect Settings Panel UI
  initSettingsModal(timer, soundboard);
});

/**
 * Wiring for the Settings Modal Panel
 */
function initSettingsModal(timer, soundboard) {
  const modal = document.getElementById('settings-modal');
  const openBtn = document.getElementById('settings-btn');
  const closeBtn = document.getElementById('close-settings-btn');
  const saveBtn = document.getElementById('save-settings-btn');
  const testChimeBtn = document.getElementById('test-chime-btn');

  // Input elements
  const inputPomo = document.getElementById('input-pomodoro');
  const inputShort = document.getElementById('input-short-break');
  const inputLong = document.getElementById('input-long-break');
  const inputChimeVol = document.getElementById('input-chime-volume');
  const labelChimeVol = document.getElementById('chime-volume-val');
  const inputDailyGoal = document.getElementById('input-daily-goal');
  const inputAutoBreaks = document.getElementById('input-auto-breaks');
  const inputAutoPomodoros = document.getElementById('input-auto-pomodoros');

  // Open Modal
  openBtn.addEventListener('click', () => {
    // Populate form with current values
    inputPomo.value = timer.durations.pomodoro / 60;
    inputShort.value = timer.durations['short-break'] / 60;
    inputLong.value = timer.durations['long-break'] / 60;
    
    inputChimeVol.value = Math.round(timer.settings.chimeVolume * 100);
    labelChimeVol.textContent = `${inputChimeVol.value}%`;
    
    inputDailyGoal.value = timer.settings.dailyGoal;
    inputAutoBreaks.checked = timer.settings.autoBreaks;
    inputAutoPomodoros.checked = timer.settings.autoPomodoros;

    modal.classList.remove('hidden');
  });

  // Close Modal
  const closeModal = () => modal.classList.add('hidden');
  closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Chime volume slider display sync
  inputChimeVol.addEventListener('input', (e) => {
    labelChimeVol.textContent = `${e.target.value}%`;
  });

  // Test Chime
  testChimeBtn.addEventListener('click', () => {
    const volume = parseFloat(inputChimeVol.value) / 100;
    soundboard.playChime(volume);
  });

  // Save Settings
  saveBtn.addEventListener('click', () => {
    const durations = {
      pomodoro: parseFloat(inputPomo.value) || 25,
      shortBreak: parseFloat(inputShort.value) || 5,
      longBreak: parseFloat(inputLong.value) || 15
    };

    const generalSettings = {
      chimeVolume: parseFloat(inputChimeVol.value) / 100,
      dailyGoal: parseInt(inputDailyGoal.value, 10) || 4,
      autoBreaks: inputAutoBreaks.checked,
      autoPomodoros: inputAutoPomodoros.checked
    };

    timer.updateSettings(durations, generalSettings);
    closeModal();
  });
}
