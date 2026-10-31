// Draw HTML pages with headless Chrome over the DevTools protocol and save each as a PNG on a
// transparent background. bake.py runs this; it needs Node 22 or newer (the built-in WebSocket).
//
//   node shoot.mjs <chrome.exe> <jobs.json>
//
// jobs.json is a list of { url, out, width, height, scale }: the page size in CSS px and the
// device pixels per CSS px. The PNG is width*scale by height*scale pixels.
//
// Why not `chrome --headless --screenshot`? Measured on Chrome 156: that route captures the first
// compositor frame, which is only partly rastered. With `--host-resolver-rules` (the offline
// guard below) a 2400x162 px page came out as its top 14 rows, every time, and with no flag it
// passed only by luck. Here the page is asked to settle (fonts, images, two animation frames) and
// the screenshot is taken again until two in a row are the same.
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import process from 'node:process';

const [chromePath, jobsPath] = process.argv.slice(2);
if (!chromePath || !jobsPath) {
  console.error('usage: node shoot.mjs <chrome.exe> <jobs.json>');
  process.exit(2);
}
if (typeof WebSocket === 'undefined') {
  console.error(`shoot.mjs needs Node 22 or newer (the built-in WebSocket); this is ${process.version}`);
  process.exit(2);
}
const jobs = JSON.parse(readFileSync(jobsPath, 'utf8'));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const within = (promise, ms, what) =>
  Promise.race([promise, new Promise((_, reject) => setTimeout(() => reject(new Error(`${what}: no answer in ${ms / 1000} s`)), ms))]);

// What a page must have finished before it is photographed.
const SETTLE = `(async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map((img) => img.decode().catch(() => {})));
  await new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)));
})()`;

const profile = mkdtempSync(join(tmpdir(), 'ozshoot-'));
const chrome = spawn(chromePath, [
  '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  // the same pixels on every machine: software raster, no LCD text, no hinting, sRGB
  '--disable-gpu', '--hide-scrollbars', '--disable-lcd-text', '--font-render-hinting=none', '--force-color-profile=srgb',
  // offline: a web font or an image from the network would make the bake depend on the internet
  '--host-resolver-rules=MAP * ~NOTFOUND', '--allow-file-access-from-files',
  '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--disable-background-networking',
  '--disable-component-update', '--disable-sync', '--mute-audio', 'about:blank',
], { stdio: 'ignore' });
let exited = false;
chrome.on('exit', () => { exited = true; });

async function endpoint() {
  const file = join(profile, 'DevToolsActivePort');
  for (let i = 0; i < 300; i++) {
    if (exited) throw new Error('Chrome exited before it opened the DevTools port');
    try {
      const [port, path] = readFileSync(file, 'utf8').trim().split(/\r?\n/);
      if (port && path) return `ws://127.0.0.1:${port}${path}`;
    } catch { /* not there yet, or Chrome still has it open for writing (EBUSY on Windows) */ }
    await sleep(100);
  }
  throw new Error('Chrome did not open the DevTools port in 30 s');
}

function connect(url) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url);
    let nextId = 1;
    const pending = new Map();
    const listeners = [];
    ws.onerror = () => reject(new Error(`cannot connect to ${url}`));
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && pending.has(msg.id)) {
        const { ok, fail, method } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) fail(new Error(`${method}: ${msg.error.message}`)); else ok(msg.result);
      } else if (msg.method) {
        listeners.forEach((fn) => fn(msg));
      }
    };
    ws.onopen = () => resolve({
      send(method, params = {}, sessionId) {
        const id = nextId++;
        ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
        return new Promise((ok, fail) => pending.set(id, { ok, fail, method }));
      },
      on: (fn) => listeners.push(fn),
      close: () => ws.close(),
    });
  });
}

async function photograph(page, job) {
  const clip = { x: 0, y: 0, width: job.width, height: job.height, scale: 1 };
  let previous = null;
  for (let i = 0; i < 20; i++) {
    const { data } = await within(page('Page.captureScreenshot', { format: 'png', clip, fromSurface: true }), 60000, 'captureScreenshot');
    if (data === previous) return Buffer.from(data, 'base64');
    previous = data;
    await sleep(60);
  }
  throw new Error(`${job.url}: the picture never settled (20 different frames in a row)`);
}

async function main() {
  const cdp = await connect(await endpoint());
  const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });
  const page = (method, params) => cdp.send(method, params, sessionId);
  let loaded = null;
  cdp.on((msg) => { if (msg.sessionId === sessionId && msg.method === 'Page.loadEventFired' && loaded) loaded(); });
  await page('Page.enable');
  for (const job of jobs) {
    await page('Emulation.setDeviceMetricsOverride', { width: job.width, height: job.height, deviceScaleFactor: job.scale, mobile: false });
    await page('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
    const done = new Promise((resolve) => { loaded = resolve; });
    await page('Page.navigate', { url: job.url });
    await within(done, 60000, `loading ${job.url}`);
    await within(page('Runtime.evaluate', { expression: SETTLE, awaitPromise: true }), 60000, `settling ${job.url}`);
    writeFileSync(job.out, await photograph(page, job));
  }
  await cdp.send('Browser.close').catch(() => {});
  cdp.close();
}

let code = 0;
try {
  await main();
} catch (err) {
  console.error(`shoot.mjs: ${err.message}`);
  code = 1;
}
chrome.kill();
for (let i = 0; i < 50 && !exited; i++) await sleep(100);
try { rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch { /* a profile left in %TEMP% is harmless */ }
process.exit(code);
