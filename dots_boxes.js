// تنظیمات ابعاد تخته (مثلاً ۳ در ۳ مربع)
const GRID_SIZE = 3;
let currentPlayer = 1; // 1: بازیکن, 2: ربات
let scores = { 1: 0, 2: 0 };
let lines = {}; // نگهداری وضعیت خطوط کشیده‌شده

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
    
    <div class="board" id="dots-board"></div>
  `;

  container.innerHTML = html;
  buildBoard();
}

function buildBoard() {
  const board = document.getElementById('dots-board');
  board.innerHTML = '';

  // ساخت شبکه‌ای از نقاط و خطوط
  for (let r = 0; r <= GRID_SIZE; r++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'board-row';

    for (let c = 0; c <= GRID_SIZE; c++) {
      // نقطه
      const dot = document.createElement('div');
      dot.className = 'dot';
      rowDiv.appendChild(dot);

      // خط افقی
      if (c < GRID_SIZE) {
        const hLine = document.createElement('div');
        hLine.className = 'line horizontal';
        hLine.dataset.id = `h_${r}_${c}`;
        hLine.onclick = () => handleLineClick(hLine);
        rowDiv.appendChild(hLine);
      }
    }
    board.appendChild(rowDiv);

    // خطوط عمودی بین ردیف‌ها
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
  
  // اگر خط قبلا کشیده شده باشد یا نوبت ربات باشد
  if (lines[lineId] || currentPlayer !== 1) return;

  // ثبت خط برای بازیکن
  drawLine(lineElem, 1);

  // در مراحل بعدی: بررسی کامل شدن مربع و نوبت ربات را اضافه می‌کنیم
}

function drawLine(elem, player) {
  lines[elem.dataset.id] = player;
  elem.classList.add('drawn', player === 1 ? 'p1' : 'p2');
}
