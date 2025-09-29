export class Radar {
  constructor(canvas, worldBounds) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.world = worldBounds; // {minX,minY,maxX,maxY}
    this.radius = Math.min(canvas.width, canvas.height) / 2 - 8;
    this.center = { x: canvas.width / 2, y: canvas.height / 2 };
  }

  worldToRadar(x, y) {
    const { minX, minY, maxX, maxY } = this.world;
    const scaleX = (x - minX) / (maxX - minX) * 2 - 1; // -1..1
    const scaleY = (y - minY) / (maxY - minY) * 2 - 1; // -1..1
    const rx = this.center.x + scaleX * this.radius;
    const ry = this.center.y + scaleY * this.radius;
    return { x: rx, y: ry };
  }

  drawBackground() {
    const { ctx, center, radius } = this;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.save();
    ctx.translate(center.x, center.y);
    // outer circle
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(0,255,153,0.35)';
    ctx.lineWidth = 2;
    ctx.stroke();
    // rings
    for (let r = radius * 0.25; r < radius; r += radius * 0.25) {
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0,255,153,0.15)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
    // cross lines
    ctx.strokeStyle = 'rgba(0,255,153,0.15)';
    ctx.beginPath();
    ctx.moveTo(-radius, 0);
    ctx.lineTo(radius, 0);
    ctx.moveTo(0, -radius);
    ctx.lineTo(0, radius);
    ctx.stroke();
    ctx.restore();
  }

  drawPlayers(players) {
    const { ctx } = this;
    for (const p of players) {
      if (!p.alive) continue;
      const pos = this.worldToRadar(p.x, p.y);
      const color = p.team === 'CT' ? '#34d399' : '#f87171';
      // body
      ctx.beginPath();
      ctx.fillStyle = color;
      ctx.arc(pos.x, pos.y, 5, 0, Math.PI * 2);
      ctx.fill();
      // yaw indicator
      const rad = (p.yaw * Math.PI) / 180;
      const len = 12;
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(pos.x + Math.cos(rad) * len, pos.y + Math.sin(rad) * len);
      ctx.strokeStyle = '#e5e7eb';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }

  render(players) {
    this.drawBackground();
    this.drawPlayers(players);
  }
}

