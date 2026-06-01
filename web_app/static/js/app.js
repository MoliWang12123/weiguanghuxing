document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.module-card,.story-card,.article-card,.wide-card,.photo-card,.message-card');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('is-visible');
    });
  }, {threshold: 0.08});
  cards.forEach(card => observer.observe(card));
});
