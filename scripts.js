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
    if (vDots.length > 0) {
      vDots.forEach((d, i) => d.classList.toggle('active', i === vIdx));
    }
  };

  vNext.addEventListener('click', () => { 
    vIdx = (vIdx + 1) % vSlides.length; 
    updateV(); 
  });
  
  vPrev.addEventListener('click', () => { 
    vIdx = (vIdx - 1 + vSlides.length) % vSlides.length; 
    updateV(); 
  });
  
  if (vDots.length > 0) {
    vDots.forEach((dot, i) => {
      dot.addEventListener('click', () => { 
        vIdx = i; 
        updateV(); 
      });
    });
  }

  // Recordatorio técnico para el Error 153 de YouTube en local
  if (window.location.protocol === 'file:') {
    console.warn("Talentópolis Info: Estás viendo la página vía file://. Los videos de YouTube podrían mostrar el Error 153. Usa un servidor local (Live Server) para verlos correctamente.");
  }
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
  }).catch(err => {
    console.error('Error al copiar al portapapeles:', err);
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
if (typeof VANTA !== 'undefined') {
  const isMobile = window.innerWidth <= 768;
  
  VANTA.NET({
    el: '.hero',
    mouseControls: !isMobile,
    touchControls: false,
    gyroControls: false,
    minHeight: 200,
    minWidth: 200,
    scale: 1.0,
    scaleMobile: 1.0,
    color: 0x0057B8,
    backgroundColor: 0x060C1A,
    points: isMobile ? 8 : 12,
    maxDistance: isMobile ? 18 : 22,
    spacing: isMobile ? 22 : 18,
    showDots: true
  });
}



/* ----------------------------------------------------------
   9. LAZY LOADING YOUTUBE FACADE CLICK HANDLER
   ---------------------------------------------------------- */
document.querySelectorAll('.youtube-facade').forEach(facade => {
  const thumb = facade.querySelector('img');
  if (thumb) {
    thumb.addEventListener('error', function() {
      this.style.opacity = '0';
      const icon = document.createElement('div');
      icon.style.cssText = 'width:80px;height:80px;border-radius:50%;background:var(--orange);color:#fff;display:flex;align-items:center;justify-content:center;font-size:2rem;position:absolute;z-index:5;';
      icon.innerHTML = '▶';
      facade.appendChild(icon);
    });
  }
  
  facade.addEventListener('click', function() {
    const videoId = this.getAttribute('data-id');
    const videoTitle = this.getAttribute('data-title') || 'Video';
    
    // Create the iframe
    const iframe = document.createElement('iframe');
    iframe.setAttribute('src', `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`);
    iframe.setAttribute('title', videoTitle);
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
    iframe.setAttribute('allowfullscreen', 'true');
    
    // Clear the facade contents and inject the iframe
    this.innerHTML = '';
    this.appendChild(iframe);
  });
});


/* ----------------------------------------------------------
   10. COMUNICARTE GUEST CAROUSEL (Interactive with Autoplay & Hover Pause)
   ---------------------------------------------------------- */
const cTrack = document.querySelector('.comunicarte-text .guest-carousel');
const cDots = document.querySelectorAll('.comunicarte-text .c-dot');
const cContainer = document.querySelector('.comunicarte-text .guest-carousel-container');

if (cTrack && cDots.length > 0) {
  let cIdx = 0;
  let autoplayInterval;

  const updateCarousel = () => {
    if (cIdx === 0) {
      cTrack.style.transform = 'translateX(0)';
    } else {
      cTrack.style.transform = 'translateX(calc(-50% - 7.5px))';
    }
    cDots.forEach((dot, idx) => {
      dot.classList.toggle('active', idx === cIdx);
    });
  };

  const nextSlide = () => {
    cIdx = (cIdx + 1) % cDots.length;
    updateCarousel();
  };

  const stopAutoplay = () => {
    if (autoplayInterval) clearInterval(autoplayInterval);
  };

  const startAutoplay = () => {
    stopAutoplay();
    autoplayInterval = setInterval(nextSlide, 5000);
  };

  // Limpieza automática del intervalo al destruir el componente
  window.addEventListener('beforeunload', stopAutoplay);

  // Click on dots
  cDots.forEach((dot, idx) => {
    dot.addEventListener('click', () => {
      cIdx = idx;
      updateCarousel();
      startAutoplay(); // Reset timer on click
    });
  });

  // Pause on hover
  if (cContainer) {
    cContainer.addEventListener('mouseenter', stopAutoplay);
    cContainer.addEventListener('mouseleave', startAutoplay);
  }

  // Also pause if hover directly on the dots area for better usability
  const dotsContainer = document.querySelector('.comunicarte-text .c-dots');
  if (dotsContainer) {
    dotsContainer.addEventListener('mouseenter', stopAutoplay);
    dotsContainer.addEventListener('mouseleave', startAutoplay);
  }

  // Initial start
  startAutoplay();
}


/* ----------------------------------------------------------
   ANTIGRAVITY POLISH — design spells
   ---------------------------------------------------------- */

/* Hero scroll indicator: aparece en hero, se desvanece al scrollear */
(function initScrollIndicator() {
  const hero = document.querySelector('.hero');
  if (!hero || document.querySelector('.hero-scroll-indicator')) return;

  const el = document.createElement('div');
  el.className = 'hero-scroll-indicator';
  el.setAttribute('aria-hidden', 'true');
  el.innerHTML = '<div class="scroll-chevron"></div><div class="scroll-chevron"></div>';
  hero.appendChild(el);

  const onScroll = () => {
    el.style.opacity = String(Math.max(0, 1 - window.scrollY / 130));
  };
  window.addEventListener('scroll', onScroll, { passive: true });
}());


/* 3D tilt en stat cards y service cards
   Solo en dispositivos con puntero preciso (mouse, no touch) y sin prefers-reduced-motion */
const isFinePointer = window.matchMedia('(pointer: fine)').matches;
const noReducedMotion = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (isFinePointer && noReducedMotion) {

  document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width  - 0.5) * 16;
      const y = ((e.clientY - r.top)  / r.height - 0.5) * -16;
      card.style.transform = `perspective(600px) translateY(-6px) rotateX(${y}deg) rotateY(${x}deg)`;
    });
    card.addEventListener('mouseleave', () => { card.style.transform = ''; });
    /* Seguridad touch: resetear si se pierde el foco */
    card.addEventListener('touchend',   () => { card.style.transform = ''; }, { passive: true });
  });

  document.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width  - 0.5) * 8;
      const y = ((e.clientY - r.top)  / r.height - 0.5) * -8;
      card.style.transform = `perspective(700px) translateY(-6px) rotateX(${y}deg) rotateY(${x}deg)`;
    });
    card.addEventListener('mouseleave', () => { card.style.transform = ''; });
    card.addEventListener('touchend',   () => { card.style.transform = ''; }, { passive: true });
  });

}

