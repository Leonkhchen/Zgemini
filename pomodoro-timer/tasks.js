/**
 * AuraFocus Task Manager Module
 */
export class TaskManager {
  constructor(onFocusChange) {
    this.tasks = [];
    this.activeFocusId = null;
    this.onFocusChange = onFocusChange; // callback to update timer banner
    
    this.estCount = 1;

    this.initDOM();
    this.loadTasks();
    this.render();
  }

  initDOM() {
    this.form = document.getElementById('add-task-form');
    this.taskInput = document.getElementById('task-input');
    this.listEl = document.getElementById('tasks-list');
    this.estCountVal = document.getElementById('est-count');
    this.estDecBtn = document.getElementById('est-dec');
    this.estIncBtn = document.getElementById('est-inc');

    this.focusBanner = document.getElementById('focus-task-banner');
    this.focusTitle = document.getElementById('focus-task-title');
    this.focusProgress = document.getElementById('focus-task-progress-text');

    this.initEventListeners();
  }

  initEventListeners() {
    // Estimator Increment/Decrement
    this.estDecBtn.addEventListener('click', () => {
      if (this.estCount > 1) {
        this.estCount--;
        this.estCountVal.textContent = this.estCount;
      }
    });

    this.estIncBtn.addEventListener('click', () => {
      if (this.estCount < 12) {
        this.estCount++;
        this.estCountVal.textContent = this.estCount;
      }
    });

    // Form submission
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = this.taskInput.value.trim();
      if (text) {
        this.addTask(text, this.estCount);
        this.taskInput.value = '';
        this.estCount = 1;
        this.estCountVal.textContent = 1;
      }
    });
  }

  loadTasks() {
    const saved = localStorage.getItem('aurafocus-tasks');
    const savedFocus = localStorage.getItem('aurafocus-active-task-id');
    
    if (saved) {
      this.tasks = JSON.parse(saved);
    }
    
    if (savedFocus) {
      this.activeFocusId = savedFocus;
      // Make sure the focused task actually exists
      const exists = this.tasks.some(t => t.id === this.activeFocusId && !t.completed);
      if (!exists) {
        this.activeFocusId = null;
        localStorage.removeItem('aurafocus-active-task-id');
      }
    }
  }

  saveTasks() {
    localStorage.setItem('aurafocus-tasks', JSON.stringify(this.tasks));
    if (this.activeFocusId) {
      localStorage.setItem('aurafocus-active-task-id', this.activeFocusId);
    } else {
      localStorage.removeItem('aurafocus-active-task-id');
    }
  }

  addTask(text, estSessions) {
    const task = {
      id: Date.now().toString(),
      text,
      estPomodoros: estSessions,
      completedPomodoros: 0,
      completed: false
    };

    this.tasks.push(task);
    
    // Automatically focus the first active task if nothing is focused
    if (!this.activeFocusId) {
      this.activeFocusId = task.id;
    }

    this.saveTasks();
    this.render();
  }

  deleteTask(id, event) {
    event.stopPropagation(); // prevent card click (focus trigger)
    
    this.tasks = this.tasks.filter(t => t.id !== id);
    
    if (this.activeFocusId === id) {
      this.activeFocusId = null;
      // fallback to next uncompleted task
      const nextTask = this.tasks.find(t => !t.completed);
      if (nextTask) {
        this.activeFocusId = nextTask.id;
      }
    }

    this.saveTasks();
    this.render();
  }

  toggleComplete(id, event) {
    event.stopPropagation(); // prevent card click (focus trigger)
    
    const task = this.tasks.find(t => t.id === id);
    if (task) {
      task.completed = !task.completed;
      
      // If task is completed and was the focused one, clear or shift focus
      if (task.completed && this.activeFocusId === id) {
        this.activeFocusId = null;
        const nextTask = this.tasks.find(t => !t.completed);
        if (nextTask) {
          this.activeFocusId = nextTask.id;
        }
      } 
      // If task is uncompleted and nothing is focused, make it focused
      else if (!task.completed && !this.activeFocusId) {
        this.activeFocusId = task.id;
      }
      
      this.saveTasks();
      this.render();
    }
  }

  setFocusTask(id) {
    const task = this.tasks.find(t => t.id === id);
    if (task && !task.completed) {
      this.activeFocusId = id;
      this.saveTasks();
      this.render();
    }
  }

  incrementCompletedPomodoro() {
    if (this.activeFocusId) {
      const task = this.tasks.find(t => t.id === this.activeFocusId);
      if (task) {
        task.completedPomodoros++;
        this.saveTasks();
        this.render();
      }
    }
  }

  getActiveFocusTask() {
    return this.tasks.find(t => t.id === this.activeFocusId);
  }

  render() {
    // Clear list
    this.listEl.innerHTML = '';

    const activeTasks = this.tasks.filter(t => !t.completed);
    const completedTasks = this.tasks.filter(t => t.completed);
    const allSortedTasks = [...activeTasks, ...completedTasks];

    if (allSortedTasks.length === 0) {
      this.listEl.innerHTML = `
        <div class="tasks-empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9 12l2 2 4-4"/>
          </svg>
          <p>No tasks yet. Add a task to start tracking your progress.</p>
        </div>
      `;
      
      // Clear center focus banner
      this.focusBanner.classList.add('empty');
      this.focusTitle.textContent = 'Select a task below to begin';
      this.focusProgress.textContent = 'Session 0/0';
      if (this.onFocusChange) this.onFocusChange(null);
      return;
    }

    allSortedTasks.forEach(task => {
      const isFocused = task.id === this.activeFocusId;
      const taskItem = document.createElement('div');
      
      taskItem.className = 'task-item';
      if (task.completed) taskItem.classList.add('completed');
      if (isFocused) taskItem.classList.add('active-focus');
      taskItem.setAttribute('data-id', task.id);

      taskItem.innerHTML = `
        <div class="task-item-left">
          <span class="custom-checkbox" title="Toggle Complete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </span>
          <span class="task-text" title="${task.text}">${task.text}</span>
        </div>
        <div class="task-item-right">
          <span class="task-pomo-count">${task.completedPomodoros}/${task.estPomodoros}</span>
          <button class="delete-task-btn" title="Delete Task" aria-label="Delete Task">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      `;

      // Event Listeners for items
      taskItem.addEventListener('click', () => {
        if (!task.completed) {
          this.setFocusTask(task.id);
        }
      });

      const checkbox = taskItem.querySelector('.custom-checkbox');
      checkbox.addEventListener('click', (e) => {
        this.toggleComplete(task.id, e);
      });

      const deleteBtn = taskItem.querySelector('.delete-task-btn');
      deleteBtn.addEventListener('click', (e) => {
        this.deleteTask(task.id, e);
      });

      this.listEl.appendChild(taskItem);
    });

    // Update Focused task banner
    const focusedTask = this.getActiveFocusTask();
    if (focusedTask) {
      this.focusBanner.classList.remove('empty');
      this.focusTitle.textContent = focusedTask.text;
      this.focusProgress.textContent = `Session ${focusedTask.completedPomodoros}/${focusedTask.estPomodoros}`;
      if (this.onFocusChange) this.onFocusChange(focusedTask);
    } else {
      this.focusBanner.classList.add('empty');
      this.focusTitle.textContent = 'Select a task below to begin';
      this.focusProgress.textContent = 'Session 0/0';
      if (this.onFocusChange) this.onFocusChange(null);
    }
  }
}
