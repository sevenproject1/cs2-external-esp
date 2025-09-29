## Mini Radar (Educational Demo)

A small Node.js + browser app that renders a radar of players updated in real-time via WebSocket. Includes a mock data simulator, no game memory access, suitable for school demos.

### Features
- Express server serving static frontend
- WebSocket endpoint broadcasting player positions ~20 Hz
- Canvas-based circular radar with team colors and yaw indicators
- Mock movement simulator (no external dependencies)

### Requirements
- Node.js 18+

### Run
```bash
npm install
npm run start
```
Open `http://localhost:3000` in your browser.

### Notes
- World bounds and map name are served from `/api/map`.
- Players are simulated server-side and broadcast to `/ws` WebSocket.
- You can adapt the server to consume an external, lawful data feed if available.

### Folder Structure
```
mini-radar/
  public/
    index.html
    main.js
    radar.js
    ws.js
  server.js
  package.json
  README.md
```

