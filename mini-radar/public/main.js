import { Radar } from './radar.js';
import { connectWebSocket } from './ws.js';

async function fetchMap() {
  const res = await fetch('/api/map', { cache: 'no-store' });
  return await res.json();
}

function setInfo(text) {
  const el = document.getElementById('info');
  if (el) el.textContent = text;
}

async function start() {
  const canvas = document.getElementById('radar');
  const map = await fetchMap();
  const radar = new Radar(canvas, map.worldBounds);
  radar.render([]);

  setInfo(`${map.name} bounds: ${map.worldBounds.minX},${map.worldBounds.minY} to ${map.worldBounds.maxX},${map.worldBounds.maxY}`);

  let lastPlayers = [];

  function animate() {
    radar.render(lastPlayers);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);

  const ws = connectWebSocket();
  ws.addEventListener('open', () => setInfo(`Connected • ${map.name}`));
  ws.addEventListener('close', () => setInfo('Disconnected'));
  ws.addEventListener('message', (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'players') {
        lastPlayers = msg.players;
      }
    } catch (e) {
      // ignore
    }
  });
}

window.addEventListener('DOMContentLoaded', start);

