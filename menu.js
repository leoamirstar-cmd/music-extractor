document.addEventListener("DOMContentLoaded", () => {
  // انیمیشن نرم ورود عناصر منو با GSAP
  gsap.from(".top-bar", { duration: 0.8, y: -30, opacity: 0, ease: "power3.out" });
  gsap.from(".section-title", { duration: 0.8, x: 30, opacity: 0, delay: 0.2, ease: "power3.out" });
  gsap.from(".featured-card", { duration: 0.8, y: 40, opacity: 0, delay: 0.3, ease: "power3.out" });
  gsap.from(".secondary-card", { duration: 0.8, y: 40, opacity: 0, delay: 0.4, ease: "power3.out" });
});

function openGame(gameId) {
  gsap.to("#main-menu", {
    duration: 0.3,
    opacity: 0,
    y: -20,
    onComplete: () => {
      document.getElementById('main-menu').classList.remove('active');
      document.getElementById('game-screen').classList.add('active');
      gsap.fromTo("#game-screen", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4 });
      
      if (gameId === 'dots-boxes') {
        initDotsAndBoxes();
      }
    }
  });
}

function showMenu() {
  gsap.to("#game-screen", {
    duration: 0.3,
    opacity: 0,
    y: 20,
    onComplete: () => {
      document.getElementById('game-screen').classList.remove('active');
      document.getElementById('main-menu').classList.add('active');
      gsap.fromTo("#main-menu", { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.4 });
    }
  });
}
