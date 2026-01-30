const searchState = document.getElementById('searchState');
const cancelledState = document.getElementById('cancelledState');
const cancelBtn = document.getElementById('cancelBtn');
const rejoinBtn = document.getElementById('rejoinBtn');
const homeBtn = document.getElementById('homeBtn');
const timerEl = document.getElementById('timer');
const queueCountEl = document.getElementById('queueCount');
const estWaitEl = document.getElementById('estWait');

let seconds = 0;
let timerInterval;
let queueInterval;

function formatTime(sec) {
  const m = String(Math.floor(sec / 60)).padStart(2, '0');
  const s = String(sec % 60).padStart(2, '0');
  return `${m}:${s}`;
}

function updateTimer() {
  seconds++;
  timerEl.textContent = formatTime(seconds);

  if (seconds < 30) estWaitEl.textContent = '~30s';
  else if (seconds < 60) estWaitEl.textContent = '~1m';
  else estWaitEl.textContent = '~2m';
}

function updateQueue() {
  queueCountEl.textContent = 247 + Math.floor(Math.random() * 20 - 10);
}

function startSearching() {
  seconds = 0;
  timerEl.textContent = '00:00';

  searchState.classList.remove('hidden');
  cancelledState.classList.remove('active');

  timerInterval = setInterval(updateTimer, 1000);
  queueInterval = setInterval(updateQueue, 3000);
}

function cancelSearching() {
  clearInterval(timerInterval);
  clearInterval(queueInterval);

  searchState.classList.add('hidden');
  cancelledState.classList.add('active');
}

cancelBtn.addEventListener('click', cancelSearching);
rejoinBtn.addEventListener('click', startSearching);
homeBtn.addEventListener('click', () => alert('Return to lobby'));

startSearching();
