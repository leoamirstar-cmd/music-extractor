document.addEventListener("DOMContentLoaded", () => {
  if (typeof gsap !== "undefined") {
    gsap.from(".top-bar", { duration: 0.6, y: -20, opacity: 0 });
    gsap.from(".featured-card", { duration: 0.6, y: 30, opacity: 0, delay: 0.2 });
  }
});

function openGame(gameId) {
  document.getElementById('main-menu').classList.remove('active');
  document.getElementById('game-screen').classList.add('active');
  
  if (gameId === 'dots-boxes') {
    // فراخوانی مستقیم تابع برای جلوگیری از صفحه سیاه
    initDotsAndBoxes();
  }
}

function showMenu() {
  document.getElementById('game-screen').classList.remove('active');
  document.getElementById('main-menu').classList.add('active');
}
