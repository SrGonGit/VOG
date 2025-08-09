function pad(n){ return n.toString().padStart(2,'0'); }

// --- Tema: aplica a preferência salva ou a do sistema antes de pintar a UI ---
(function() {
  try {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldDark = saved ? saved === 'dark' : prefersDark;
    document.addEventListener('DOMContentLoaded', () => {
      document.body.classList.toggle('dark-theme', shouldDark);
      const btn = document.getElementById('themeToggle');
      if (btn) btn.textContent = shouldDark ? '🌞' : '🌙';
    });
  } catch(e) {}
})();

function tickCounter(el){
  const startIso = el.getAttribute('data-start');
  const start = new Date(startIso);
  function render(){
    const now = new Date();
    let diff = Math.floor((now - start) / 1000); // s
    const years = Math.floor(diff / (365*24*3600)); diff -= years*365*24*3600;
    const days = Math.floor(diff / (24*3600)); diff -= days*24*3600;
    const hours = Math.floor(diff / 3600); diff -= hours*3600;
    const mins = Math.floor(diff / 60); diff -= mins*60;
    const secs = diff;
    el.textContent = `${years} anos, ${days} dias, ${pad(hours)}:${pad(mins)}:${pad(secs)}`;
  }
  render();
  setInterval(render, 1000);
}

document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('counter');
  if (el) tickCounter(el);
});
