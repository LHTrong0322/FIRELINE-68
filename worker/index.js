// Tuyến Lửa – máy chủ online (Cloudflare Worker + Durable Object)
// Mỗi mã phòng là một Durable Object, chuyển tiếp trạng thái người chơi qua WebSocket.
import { DurableObject } from "cloudflare:workers";

export class GameRoom extends DurableObject {
  async fetch(request) {
    const url = new URL(request.url);
    // ---- sảnh: danh sách phòng đang mở (một Durable Object riêng tên "__lobby__")
    if (url.pathname === "/lobby/set") {
      const b = await request.json().catch(() => null); if (!b || typeof b.room !== "string") return new Response("bad", { status: 400 });
      const rooms = (await this.ctx.storage.get("rooms")) || {};
      if (b.n > 0) rooms[b.room] = { n: Math.min(16, b.n | 0), title: String(b.title || "").slice(0, 40), t: Date.now() }; else delete rooms[b.room];
      await this.ctx.storage.put("rooms", rooms); return new Response("ok");
    }
    if (url.pathname === "/lobby/list") {
      const rooms = (await this.ctx.storage.get("rooms")) || {}; const now = Date.now(); let changed = false;
      for (const k in rooms) if (now - rooms[k].t > 2 * 60 * 1000) { delete rooms[k]; changed = true; }  // phòng không báo danh 2 phút = đã đóng
      if (changed) await this.ctx.storage.put("rooms", rooms);
      const list = Object.entries(rooms).map(([room, r]) => ({ room, n: r.n, title: r.title })).sort((a, b) => b.n - a.n).slice(0, 40);
      return new Response(JSON.stringify(list), { headers: { "content-type": "application/json", "cache-control": "no-store" } });
    }
    const sockets = this.ctx.getWebSockets();
    if (sockets.length >= 16) return new Response("Phòng đã đầy", { status: 429 });
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    this.ctx.acceptWebSocket(server);
    const id = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
    server.serializeAttachment({ id, p: null });
    const peers = sockets.map((w) => w.deserializeAttachment()).filter((a) => a && a.p);
    server.send(JSON.stringify({ t: "hello", id, peers }));
    const room = (url.searchParams.get("room") || "").toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 60), title = (url.searchParams.get("title") || "").replace(/[<>]/g, "").slice(0, 40);
    if (room) { const old = (await this.ctx.storage.get("meta")) || {}; await this.ctx.storage.put("meta", { room, title: old.title || title }); }
    await this.report(sockets.length + 1);
    if (!(await this.ctx.storage.getAlarm())) await this.ctx.storage.setAlarm(Date.now() + 45000);
    return new Response(null, { status: 101, webSocket: client });
  }
  // nhịp báo danh mỗi 45 giây: giữ phòng trong sảnh khi còn người, tự gỡ khi hết người
  async alarm() {
    const n = this.ctx.getWebSockets().filter((w) => w.readyState === 1).length;
    await this.report(n);
    if (n > 0) await this.ctx.storage.setAlarm(Date.now() + 45000);
  }
  async report(n) {
    try {
      const meta = await this.ctx.storage.get("meta"); if (!meta || !this.env || !this.env.ROOMS) return;
      if (n <= 0) await this.ctx.storage.delete("meta");
      await this.env.ROOMS.get(this.env.ROOMS.idFromName("__lobby__")).fetch("https://lobby/lobby/set", { method: "POST", body: JSON.stringify({ room: meta.room, title: meta.title, n }) });
    } catch (e) {}
  }
  broadcast(from, text) {
    for (const w of this.ctx.getWebSockets()) if (w !== from) { try { w.send(text); } catch (e) {} }
  }
  webSocketMessage(ws, msg) {
    if (typeof msg !== "string") {
      // giọng nói: gói âm thanh nhị phân (μ-law 16kHz), gắn mã người gửi rồi chuyển cho người khác
      const data = msg instanceof ArrayBuffer ? new Uint8Array(msg) : null;
      if (!data || data.byteLength === 0 || data.byteLength > 4096) return;
      const a = ws.deserializeAttachment(); if (!a) return;
      const out = new Uint8Array(12 + data.byteLength);
      for (let i = 0; i < 12; i++) out[i] = a.id.charCodeAt(i) || 32;
      out.set(data, 12);
      for (const w of this.ctx.getWebSockets()) if (w !== ws) { try { w.send(out); } catch (e) {} }
      return;
    }
    if (msg.length > 6000) return;
    let m; try { m = JSON.parse(msg); } catch (e) { return; }
    if (m.t !== "p" || typeof m.d !== "object" || m.d === null) return;
    const a = ws.deserializeAttachment(); if (!a) return;
    a.p = m.d; ws.serializeAttachment(a);
    this.broadcast(ws, JSON.stringify({ t: "p", id: a.id, d: m.d }));
  }
  async webSocketClose(ws, code) {
    const a = ws.deserializeAttachment();
    if (a) this.broadcast(ws, JSON.stringify({ t: "l", id: a.id }));
    try { ws.close(1000, "bye"); } catch (e) {}
    await this.report(this.ctx.getWebSockets().filter((w) => w !== ws && w.readyState === 1).length);
  }
  webSocketError(ws) { this.webSocketClose(ws); }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/ws") {
      if (request.headers.get("Upgrade") !== "websocket") return new Response("Cần WebSocket", { status: 426 });
      const room = (url.searchParams.get("room") || "lobby").toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 60) || "lobby";
      if (room === "__lobby__") return new Response("no", { status: 403 });
      return env.ROOMS.get(env.ROOMS.idFromName(room)).fetch(request);
    }
    if (url.pathname === "/rooms") {
      return env.ROOMS.get(env.ROOMS.idFromName("__lobby__")).fetch(new Request("https://lobby/lobby/list"));
    }
    const res = await env.ASSETS.fetch(request);
    // trang game luôn lấy bản mới nhất (tránh điện thoại giữ bản cũ)
    if (url.pathname === "/" || url.pathname.endsWith(".html") || url.pathname.endsWith(".webmanifest")) {
      const r = new Response(res.body, res); r.headers.set("Cache-Control", "no-cache, must-revalidate"); return r;
    }
    return res;
  },
};
