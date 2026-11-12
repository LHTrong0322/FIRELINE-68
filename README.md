# FIRELINE '68 · Tuyến Lửa

Game FPS 3D chạy trên trình duyệt (PC + mobile xoay ngang). Bộ đội giữ căn cứ ngầm trước các đợt tấn công, có chế độ đấu online theo mã phòng.

- `public/index.html` – toàn bộ game (Three.js, đồ hoạ PBR tạo bằng GPU)
- `worker/index.js` – máy chủ online (Cloudflare Worker + Durable Object, WebSocket)
- `wrangler.toml` – cấu hình deploy Cloudflare

Agent build by @Trong0322
