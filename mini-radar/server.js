import express from 'express';
import http from 'http';
import cors from 'cors';
import { WebSocketServer } from 'ws';

const app = express();
app.use(cors());
app.use(express.json());

// Serve static frontend
app.use(express.static('public'));

// Simple map metadata endpoint
app.get('/api/map', (req, res) => {
  res.json({
    name: 'de_demo',
    worldBounds: { minX: -2500, minY: -2500, maxX: 2500, maxY: 2500 },
  });
});

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

const clients = new Set();
wss.on('connection', (ws) => {
  clients.add(ws);
  ws.on('close', () => clients.delete(ws));
});

// Mock state: 5 players moving around
const numPlayers = 5;
const players = Array.from({ length: numPlayers }).map((_, idx) => ({
  id: `p${idx + 1}`,
  team: idx % 2 === 0 ? 'T' : 'CT',
  x: (Math.random() - 0.5) * 3000,
  y: (Math.random() - 0.5) * 3000,
  yaw: Math.random() * 360,
  alive: true,
}));

function stepSimulation(deltaSeconds) {
  for (const p of players) {
    const speed = 150; // units per second
    const dir = (Math.random() * 2 - 1) * 45; // jitter around current yaw
    p.yaw = (p.yaw + dir * deltaSeconds) % 360;
    const rad = (p.yaw * Math.PI) / 180;
    p.x += Math.cos(rad) * speed * deltaSeconds;
    p.y += Math.sin(rad) * speed * deltaSeconds;
    // keep in bounds
    if (p.x < -2400 || p.x > 2400) {
      p.yaw = 180 - p.yaw;
    }
    if (p.y < -2400 || p.y > 2400) {
      p.yaw = -p.yaw;
    }
  }
}

function broadcastState() {
  const payload = JSON.stringify({
    type: 'players',
    timestamp: Date.now(),
    players,
  });
  for (const ws of clients) {
    if (ws.readyState === ws.OPEN) {
      ws.send(payload);
    }
  }
}

let last = Date.now();
setInterval(() => {
  const now = Date.now();
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  stepSimulation(dt);
  broadcastState();
}, 1000 / 20); // 20 Hz updates

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Mini radar server running on http://localhost:${PORT}`);
});

