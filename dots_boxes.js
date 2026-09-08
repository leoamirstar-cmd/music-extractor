const GRID_SIZE = 3;
let currentPlayer = 1; // 1: بازیکن, 2: ربات
let scores = { 1: 0, 2: 0 };
let lines = {};

function initDotsAndBoxes() {
  const container = document.getElementById('board-container');
  scores = { 1: 0, 2: 0 };
  currentPlayer = 1;
  lines = {};

  let html = `
    <div class="game-status">
      <div class="player-score p1 active" id="score-p1">
        <span>شما</span>
        <strong id="p1-val">0</strong>
      </div>
      <div class="turn-indicator" id="turn-text">نوبت شماست</div>
      <div class="player-score p2" id="score-p2">
        <span>ربات</span>
        <strong id="p2-val">0</strong>
      </div>
    </div>
    
    <div id="dots-board"></div>
  `;

  container.innerHTML = html;
  buildBoard();
}

function buildBoard() {
  const board = document.getElementById('dots-board');
  board.innerHTML = '';

  for (let r = 0; r <= GRID_SIZE; r++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'board-row';

    for (let c = 0; c <= GRID_SIZE; c++) {
      const dot = document.createElement('div');
      dot.className = 'dot';
      rowDiv.appendChild(dot);

      if (c < GRID_SIZE) {
        const hLine = document.createElement('div');
        hLine.className = 'line horizontal';
        hLine.dataset.id = `h_${r}_${c}`;
        hLine.onclick = () => handleLineClick(hLine);
        rowDiv.appendChild(hLine);
      }
    }
    board.appendChild(rowDiv);

    if (r < GRID_SIZE) {
      const vRowDiv = document.createElement('div');
      vRowDiv.className = 'board-row vertical-row';

      for (let c = 0; c <= GRID_SIZE; c++) {
        const vLine = document.createElement('div');
        vLine.className = 'line vertical';
        vLine.dataset.id = `v_${r}_${c}`;
        vLine.onclick = () => handleLineClick(vLine);
        vRowDiv.appendChild(vLine);

        if (c < GRID_SIZE) {
          const box = document.createElement('div');
          box.className = 'box';
          box.id = `box_${r}_${c}`;
          vRowDiv.appendChild(box);
        }
      }
      board.appendChild(vRowDiv);
    }
  }
}

function handleLineClick(lineElem) {
  const lineId = lineElem.dataset.id;
  if (lines[lineId] || currentPlayer !== 1) return;

  makeMove(lineElem);
}

function makeMove(lineElem) {
  const lineId = lineElem.dataset.id;
  lines[lineId] = currentPlayer;
  lineElem.classList.add('drawn', currentPlayer === 1 ? 'p1' : 'p2');

  const completedBoxes = checkBoxes();

  if (completedBoxes > 0) {
    scores[currentPlayer] += completedBoxes;
    updateUI();
    
    if (scores[1] + scores[2] === GRID_SIZE * GRID_SIZE) {
      setTimeout(endGame, 300);
      return;
    }

    if (currentPlayer === 2) {
      setTimeout(botTurn, 600);
    }
  } else {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
    updateUI();

    if (currentPlayer === 2) {
      setTimeout(botTurn, 600);
    }
  }
}

function checkBoxes() {
  let madeBox = 0;
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const box = document.getElementById(`box_${r}_${c}`);
      if (!box.classList.contains('p1') && !box.classList.contains('p2')) {
        const top = lines[`h_${r}_${c}`];
        const bottom = lines[`h_${r+1}_${c}`];
        const left = lines[`v_${r}_${c}`];
        const right = lines[`v_${r}_${c+1}`];

        if (top && bottom && left && right) {
          box.classList.add(currentPlayer === 1 ? 'p1' : 'p2');
          madeBox++;
        }
      }
    }
  }
  return madeBox;
}

function updateUI() {
  document.getElementById('p1-val').innerText = scores[1];
  document.getElementById('p2-val').innerText = scores[2];

  const p1Box = document.getElementById('score-p1');
  const p2Box = document.getElementById('score-p2');
  const turnText = document.getElementById('turn-text');

  if (currentPlayer === 1) {
    p1Box.classList.add('active');
    p2Box.classList.remove('active');
    turnText.innerText = 'نوبت شماست';
  } else {
    p2Box.classList.add('active');
    p1Box.classList.remove('active');
    turnText.innerText = 'نوبت ربات...';
  }
}

function botTurn() {
  if (currentPlayer !== 2) return;

  const availableLines = Array.from(document.querySelectorAll('.line:not(.drawn)'));
  if (availableLines.length === 0) return;

  // انتخاب تصادفی یک خط خالی توسط ربات
  const randomLine = availableLines[Math.floor(Math.random() * availableLines.length)];
  makeMove(randomLine);
}

function endGame() {
  let winnerText = scores[1] > scores[2] ? '🎉 شما برنده شدید!' : (scores[2] > scores[1] ? '🤖 ربات برنده شد!' : '🤝 مساوی شدید!');
  alert(`پایان بازی!\n${winnerText}\nامتیاز شما: ${scores[1]} | امتیاز ربات: ${scores[2]}`);
}
