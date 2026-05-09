/* ============================================================
   scripts.js — Talentópolis
   ============================================================ */

/* ----------------------------------------------------------
   1. FADE-UP ANIMATIONS (IntersectionObserver)
   ---------------------------------------------------------- */
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));


/* ----------------------------------------------------------
   2. NAVBAR — cambio de fondo al hacer scroll
   ---------------------------------------------------------- */
const header = document.querySelector('.header');
window.addEventListener('scroll', () => {
  if (header) {
    header.classList.toggle('scrolled', window.scrollY > 50);
  }
});


/* ----------------------------------------------------------
   2.1 MOBILE MENU TOGGLE
   ---------------------------------------------------------- */
const menuToggle = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobileMenu');
const body = document.body;

if (menuToggle && mobileMenu) {
  const toggleMenu = () => {
    menuToggle.classList.toggle('open');
    mobileMenu.classList.toggle('open');
    body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
  };

  menuToggle.addEventListener('click', toggleMenu);

  // Close menu when clicking a link
  mobileMenu.querySelectorAll('.mobile-link').forEach(link => {
    link.addEventListener('click', () => {
      menuToggle.classList.remove('open');
      mobileMenu.classList.remove('open');
      body.style.overflow = '';
    });
  });

  // Close menu on resize if wider than 900px
  window.addEventListener('resize', () => {
    if (window.innerWidth > 900 && mobileMenu.classList.contains('open')) {
      menuToggle.classList.remove('open');
      mobileMenu.classList.remove('open');
      body.style.overflow = '';
    }
  });
}


/* ----------------------------------------------------------
   3. GALERÍA DE FOTOS (Invitados)
   ---------------------------------------------------------- */
const track = document.getElementById('galleryTrack');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
let gIdx = 0;

if (track && prevBtn && nextBtn) {
  const slides = track.querySelectorAll('.gallery-slide');
  const update = () => { track.style.transform = `translateX(-${gIdx * 100}%)`; };
  nextBtn.addEventListener('click', () => { gIdx = (gIdx + 1) % slides.length; update(); });
  prevBtn.addEventListener('click', () => { gIdx = (gIdx - 1 + slides.length) % slides.length; update(); });
}


/* ----------------------------------------------------------
   4. GALERÍA DE VIDEOS (Brochure)
   ---------------------------------------------------------- */
const vTrack = document.getElementById('videoBrochureTrack');
const vPrev  = document.getElementById('prevBrochureVideoBtn');
const vNext  = document.getElementById('nextBrochureVideoBtn');
const vDots  = document.querySelectorAll('#vgDots .vg-dot');
let vIdx = 0;

if (vTrack && vPrev && vNext) {
  const vSlides = vTrack.querySelectorAll('.gallery-slide-full');

  const updateV = () => {
    vTrack.style.transform = `translateX(-${vIdx * 100}%)`;
    vDots.forEach((d, i) => d.classList.toggle('active', i === vIdx));
  };

  vNext.addEventListener('click', () => { vIdx = (vIdx + 1) % vSlides.length; updateV(); });
  vPrev.addEventListener('click', () => { vIdx = (vIdx - 1 + vSlides.length) % vSlides.length; updateV(); });
  vDots.forEach((dot, i) => dot.addEventListener('click', () => { vIdx = i; updateV(); }));
}


/* ----------------------------------------------------------
   5. COPIAR AL PORTAPAPELES con toast de feedback
   ---------------------------------------------------------- */
function copyToClipboard(text, el) {
  navigator.clipboard.writeText(text).then(() => {
    const toast = document.createElement('div');
    toast.innerText = '¡Copiado!';
    toast.className = 'copy-toast';
    el.appendChild(toast);
    setTimeout(() => toast.remove(), 1500);
  });
}


/* ----------------------------------------------------------
   6. CONTADOR ANIMADO — Stat Cards
   ---------------------------------------------------------- */
function animateCounter(el) {
  const raw    = el.textContent.trim();
  const prefix = raw.match(/^[+]?/)?.[0] || '';
  const numStr = raw.replace(/[^0-9.,KkMm]/g, '');
  let   target, suffix = '';

  if (/[Kk]$/.test(numStr)) {
    target = parseFloat(numStr) * 1000;
    suffix = 'K';
  } else if (/[Mm]$/.test(numStr)) {
    target = parseFloat(numStr) * 1000000;
    suffix = 'M';
  } else {
    target = parseFloat(numStr.replace(',', '.')) || 0;
  }

  const duration = 1800;
  const start    = performance.now();

  const tick = (now) => {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease     = 1 - Math.pow(1 - progress, 4);
    const value    = Math.round(target * ease);

    if (suffix === 'K') {
      el.textContent = `+${(value / 1000).toFixed(1)}K`;
    } else if (suffix === 'M') {
      el.textContent = `+${(value / 1000000).toFixed(1)}M`;
    } else {
      el.textContent = `${prefix}${value.toLocaleString('es-CL')}`;
    }

    if (progress < 1) requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);
}

const statObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      statObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-card .number').forEach(el => {
  statObserver.observe(el);
});


/* ----------------------------------------------------------
   7. VANTA.NET — Fondo animado Hero
   ---------------------------------------------------------- */
const isMobile = window.matchMedia('(max-width: 768px)').matches;

if (!isMobile && typeof VANTA !== 'undefined') {
  VANTA.NET({
    el: '.hero',
    mouseControls: true,
    touchControls: false,
    gyroControls: false,
    minHeight: 200,
    minWidth: 200,
    scale: 1.0,
    scaleMobile: 1.0,
    color: 0x0057B8,
    backgroundColor: 0x060C1A,
    points: 12,
    maxDistance: 22,
    spacing: 18,
    showDots: true
  });
}


/* ----------------------------------------------------------
   8. DESCARGA FORZADA DEL DOSSIER
   ---------------------------------------------------------- */
function downloadDossier(e) {
  e.preventDefault();
  const url = 'assets/Brochure_Talentopolis_2026.pdf';
  const filename = 'Brochure_Talentopolis_2026.pdf';

  fetch(url)
    .then(res => {
      if (!res.ok) throw new Error('fetch failed');
      return res.blob();
    })
    .then(blob => {
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
    })
    .catch(() => {
      window.open(url, '_blank');
    });
}
