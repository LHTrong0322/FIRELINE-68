// Tuyến Lửa – máy chủ online (Cloudflare Worker + Durable Object)
// Mỗi mã phòng là một Durable Object, chuyển tiếp trạng thái người chơi qua WebSocket.
import { DurableObject } from "cloudflare:workers";

export class GameRoom extends DurableObject {
  async fetch(request) {
    const sockets = this.ctx.getWebSockets();
    if (sockets.length >= 16) return new Response("Phòng đã đầy", { status: 429 });
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    this.ctx.acceptWebSocket(server);
    const id = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
    server.serializeAttachment({ id, p: null });
    const peers = sockets.map((w) => w.deserializeAttachment()).filter((a) => a && a.p);
    server.send(JSON.stringify({ t: "hello", id, peers }));
    return new Response(null, { status: 101, webSocket: client });
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
  webSocketClose(ws, code) {
    const a = ws.deserializeAttachment();
    if (a) this.broadcast(ws, JSON.stringify({ t: "l", id: a.id }));
    try { ws.close(1000, "bye"); } catch (e) {}
  }
  webSocketError(ws) { this.webSocketClose(ws); }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/ws") {
      if (request.headers.get("Upgrade") !== "websocket") return new Response("Cần WebSocket", { status: 426 });
      const room = (url.searchParams.get("room") || "lobby").toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 40) || "lobby";
      return env.ROOMS.get(env.ROOMS.idFromName(room)).fetch(request);
    }
    return env.ASSETS.fetch(request);
  },
};
