const puppeteer = require('puppeteer');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const urlMod = require('url');

const WIDTH  = 1920;
const HEIGHT = 1080;
const PORT   = 18765;
const OUTPUT = path.resolve(__dirname, 'Brochure_Talentopolis_2026.pdf');

const SECTIONS = [
  'hero',
  'workflow',
  'about',
  'services',
  'programs',
  'videos',
  'spotify',
  'team',
  'galeria-invitados',
  'comunicarte',
  'deliverables',
  'contact',
];

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css',
  '.js':   'application/javascript',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
  '.ico':  'image/x-icon',
  '.mp4':  'video/mp4',
  '.webm': 'video/webm',
  '.webp': 'image/webp',
};

function startServer(rootDir, port) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const parsed = urlMod.parse(req.url);
      const filePath = path.join(rootDir, decodeURIComponent(parsed.pathname));

      if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        res.writeHead(404); res.end('Not found'); return;
      }

      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
      fs.createReadStream(filePath).pipe(res);
    });

    server.listen(port, '127.0.0.1', () => resolve(server));
    server.on('error', reject);
  });
}

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  // ── Servidor HTTP local ──────────────────────────────────────────
  console.log(`🌐 Iniciando servidor HTTP local en puerto ${PORT}...`);
  const server = await startServer(__dirname, PORT);
  const PAGE_URL = `http://127.0.0.1:${PORT}/index.html`;

  console.log('🚀 Iniciando Puppeteer...');

  const userDataDir = path.join(os.tmpdir(), `puppeteer-pdf-${Date.now()}`);

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    userDataDir,
    args: [
      `--window-size=${WIDTH},${HEIGHT}`,
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--force-device-scale-factor=1',
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 2 });

  console.log('📄 Cargando página...');
  await page.goto(PAGE_URL, { waitUntil: 'networkidle0', timeout: 60000 });
  await wait(3500);

  // ── CSS: neutralizar scroll-snap, animaciones y forzar alturas ──
  await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
      html, body {
        scroll-snap-type: none !important;
        overflow-y: scroll !important;
        height: auto !important;
      }
      section, .section, .hero, .contact-section-full {
        scroll-snap-align: none !important;
        scroll-snap-stop: normal !important;
        height: 100vh !important;
        min-height: 100vh !important;
        overflow: hidden !important;
      }
      * {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
      .fade-up {
        opacity: 1 !important;
        transform: translateY(0) !important;
        visibility: visible !important;
      }
    `;
    document.head.appendChild(style);

    document.querySelectorAll('.fade-up').forEach(el => {
      el.classList.add('visible');
      el.style.cssText += 'opacity:1!important;transform:none!important;';
    });

    if (window.VANTA && window.VANTA._instances) {
      window.VANTA._instances.forEach(v => { try { v.destroy(); } catch(e){} });
    }
  });

  await wait(600);

  // ── Primera pasada: activar lazy-load en cada sección ───────────
  console.log('🔄 Activando secciones...');
  for (const id of SECTIONS) {
    await page.evaluate(sectionId => {
      const el = document.getElementById(sectionId);
      if (el) window.scrollTo({ top: el.offsetTop, behavior: 'instant' });
    }, id);
    await wait(350);
    await page.evaluate(() => {
      document.querySelectorAll('.fade-up').forEach(el => {
        el.classList.add('visible');
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
    });
  }

  await wait(500);

  // ── Obtener offsetTop de cada sección ───────────────────────────
  const offsets = {};
  for (const id of SECTIONS) {
    const top = await page.evaluate(sectionId => {
      const el = document.getElementById(sectionId);
      if (!el) return null;
      el.getBoundingClientRect();
      return Math.round(el.offsetTop);
    }, id);
    offsets[id] = top;
  }

  const screenshots = [];

  // ── Segunda pasada: captura con clip en coordenadas absolutas ───
  for (const id of SECTIONS) {
    const offsetTop = offsets[id];

    if (offsetTop === null) {
      console.warn(`⚠️  #${id} no encontrada, omitiendo.`);
      continue;
    }

    const buffer = await page.screenshot({
      type: 'png',
      clip: { x: 0, y: offsetTop, width: WIDTH, height: HEIGHT },
    });

    screenshots.push(buffer);
    console.log(`✅  #${id}  (y: ${offsetTop}px)`);
  }

  await browser.close();
  server.close();
  try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch(e) {}

  // ── Construir PDF ────────────────────────────────────────────────
  console.log('\n📦 Construyendo PDF horizontal...');
  const pdfDoc = await PDFDocument.create();

  for (let i = 0; i < screenshots.length; i++) {
    const pngImage = await pdfDoc.embedPng(screenshots[i]);
    const pageW = 841.89;
    const pageH = pageW * (HEIGHT / WIDTH);
    const pdfPage = pdfDoc.addPage([pageW, pageH]);
    pdfPage.drawImage(pngImage, { x: 0, y: 0, width: pageW, height: pageH });
    console.log(`   Página ${i + 1} / ${screenshots.length} añadida`);
  }

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(OUTPUT, pdfBytes);

  console.log(`\n🎉 PDF listo:`);
  console.log(`   ${OUTPUT}`);
  console.log(`   ${screenshots.length} páginas · 16:9 · 2× resolución`);
})();
