function openGame(gameId) {
  document.getElementById('main-menu').classList.remove('active');
  document.getElementById('game-screen').classList.add('active');
  
  if (gameId === 'dots-boxes') {
    initDotsAndBoxes();
  }
}

function showMenu() {
  document.getElementById('game-screen').classList.remove('active');
  document.getElementById('main-menu').classList.add('active');
}

