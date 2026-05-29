const puppeteer = require('puppeteer');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const urlMod = require('url');

const WIDTH  = 1920;
const HEIGHT = 1080;
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

// Localizador inteligente y multiplataforma del ejecutable de Google Chrome
function findChromeExecutable() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) {
    console.log(`🔍 Usando Chrome desde la variable CHROME_PATH: ${process.env.CHROME_PATH}`);
    return process.env.CHROME_PATH;
  }

  const platform = os.platform();
  if (platform === 'win32') {
    const paths = [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      path.join(process.env.LOCALAPPDATA || '', 'Google\\Chrome\\Application\\chrome.exe')
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) {
        console.log(`🔍 Chrome detectado en Windows: ${p}`);
        return p;
      }
    }
  } else if (platform === 'darwin') {
    const paths = [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) {
        console.log(`🔍 Chrome detectado en macOS: ${p}`);
        return p;
      }
    }
  }

  console.log('⚠️  No se encontró instalación de Chrome local en las rutas estándar. Se usará el ejecutable por defecto de Puppeteer.');
  return undefined; // Puppeteer usará su ejecutable por defecto
}

function startServer(rootDir) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const parsed = urlMod.parse(req.url);
      const filePath = path.join(rootDir, decodeURIComponent(parsed.pathname));

      // Security Fix: Prevent Path Traversal
      if (!filePath.startsWith(rootDir)) {
        res.writeHead(403); res.end('Forbidden'); return;
      }

      if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        res.writeHead(404); res.end('Not found'); return;
      }

      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
      fs.createReadStream(filePath).pipe(res);
    });

    // Escuchar en el puerto 0 para asignación dinámica y evitar colisiones de puertos (EADDRINUSE)
    server.listen(0, '127.0.0.1', () => resolve(server));
    server.on('error', reject);
  });
}

const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  let server = null;
  let browser = null;
  const userDataDir = path.join(os.tmpdir(), `puppeteer-pdf-${Date.now()}`);

  try {
    // 1. Iniciar el servidor local HTTP en puerto dinámico
    console.log('🌐 Iniciando servidor HTTP local en puerto dinámico...');
    server = await startServer(__dirname);
    const PORT = server.address().port;
    const PAGE_URL = `http://127.0.0.1:${PORT}/index.html`;
    console.log(`✅ Servidor HTTP local corriendo en: http://127.0.0.1:${PORT}`);

    // 2. Localizar Chrome e iniciar Puppeteer
    console.log('🚀 Iniciando Puppeteer...');
    const executablePath = findChromeExecutable();

    const launchOptions = {
      headless: 'new',
      userDataDir,
      args: [
        `--window-size=${WIDTH},${HEIGHT}`,
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--force-device-scale-factor=1',
      ],
    };

    if (executablePath) {
      launchOptions.executablePath = executablePath;
    }

    browser = await puppeteer.launch(launchOptions);
    console.log('✅ Puppeteer iniciado correctamente.');

    const page = await browser.newPage();
    await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 2 });

    console.log('📄 Cargando página index.html...');
    await page.goto(PAGE_URL, { waitUntil: 'networkidle0', timeout: 60000 });
    await wait(3500);

    // ── CSS: neutralizar scroll-snap, animaciones y forzar alturas ──
    console.log('🛠️  Aplicando estilos de preparación para captura estática...');
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

      // Detener cualquier efecto Vanta.js de fondo para evitar parpadeos
      if (window.VANTA && window.VANTA._instances) {
        window.VANTA._instances.forEach(v => { try { v.destroy(); } catch(e){} });
      }
    });

    await wait(600);

    // ── Primera pasada: activar lazy-load en cada sección ───────────
    console.log('🔄 Activando secciones (desplazamiento previo)...');
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
        return Math.round(el.offsetTop);
      }, id);
      offsets[id] = top;
    }

    const screenshots = [];

    // ── Segunda pasada: captura con clip en coordenadas absolutas ───
    console.log('📸 Capturando vistas de alta resolución...');
    for (const id of SECTIONS) {
      const offsetTop = offsets[id];

      if (offsetTop === null) {
        console.warn(`⚠️  Sección #${id} no encontrada, omitiendo.`);
        continue;
      }

      const buffer = await page.screenshot({
        type: 'jpeg',
        quality: 90,
        clip: { x: 0, y: offsetTop, width: WIDTH, height: HEIGHT },
      });

      screenshots.push(buffer);
      console.log(`✅  Sección #${id} capturada en formato JPEG (y: ${offsetTop}px)`);
    }

    // ── Construir PDF ────────────────────────────────────────────────
    console.log('\n📦 Construyendo documento PDF horizontal...');
    const pdfDoc = await PDFDocument.create();

    // Establecer metadatos profesionales del documento PDF
    pdfDoc.setTitle("Talentópolis — Brochure Corporativa 2026");
    pdfDoc.setAuthor("Talentópolis");
    pdfDoc.setSubject("Dossier de Servicios y Soluciones Audiovisuales");
    pdfDoc.setCreator("Talentópolis PDF Engine");
    pdfDoc.setProducer("Talentópolis SpA");

    for (let i = 0; i < screenshots.length; i++) {
      const jpgImage = await pdfDoc.embedJpg(screenshots[i]);
      const pageW = 841.89;
      const pageH = pageW * (HEIGHT / WIDTH);
      const pdfPage = pdfDoc.addPage([pageW, pageH]);
      pdfPage.drawImage(jpgImage, { x: 0, y: 0, width: pageW, height: pageH });
      console.log(`   Página ${i + 1} / ${screenshots.length} añadida.`);
    }

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync(OUTPUT, pdfBytes);

    console.log(`\n🎉 ¡Brochure PDF generado con éxito absoluto!`);
    console.log(`   Ruta: ${OUTPUT}`);
    console.log(`   Detalles: ${screenshots.length} páginas · Relación 16:9 · Resolución 2×`);

  } catch (error) {
    console.error('❌ ERROR CRÍTICO durante la generación del PDF:', error);
    process.exitCode = 1;
  } finally {
    // Ciclo de vida indestructible: Liberación absoluta de puertos y recursos zombie
    console.log('\n🧹 Iniciando ciclo de limpieza de recursos...');
    if (browser) {
      try {
        console.log('   Cerrando instancia de Puppeteer...');
        await browser.close();
      } catch (e) {
        console.error('   Error cerrando Puppeteer:', e);
      }
    }
    if (server) {
      try {
        console.log('   Deteniendo servidor HTTP local...');
        server.close();
      } catch (e) {
        console.error('   Error cerrando servidor HTTP:', e);
      }
    }
    try {
      if (fs.existsSync(userDataDir)) {
        console.log('   Eliminando directorio temporal de datos del usuario...');
        fs.rmSync(userDataDir, { recursive: true, force: true });
      }
    } catch (e) {
      console.error('   Error eliminando directorio temporal:', e);
    }
    console.log('🧹 Limpieza de recursos completada.');
  }
})();
