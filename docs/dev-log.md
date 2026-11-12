# Nhật ký QA & nâng cấp lối chơi FIRELINE '68

## 2026-11-12
- LỖI: đốm đen mờ che màn hình khi địch bắn trúng quanh người chơi. Nguyên nhân: hạt bụi/khói/máu mờ dần bằng cách làm tối màu (NormalBlending) thay vì giảm alpha. ĐÃ SỬA: màu RGBA, alpha mờ dần.
- LỖI tiềm ẩn: điểm phản chiếu đèn trên vũng nước vượt giới hạn HalfFloat thành Inf/NaN và bị bloom loang thành ô đen. ĐÃ SỬA: `SanitizeShader` trước GTAO và bloom; độ nhám vũng nước tối thiểu 0.12.
- Ẩn tâm ngắm khi hy sinh (trước đó đè lên chữ ở màn hình kết thúc).
- LỖI: nút VÀO PHÒNG không hoạt động trên máy chậm, bước kiểm tra kết nối đếm số lần chờ thay vì thời gian thật (có thể treo hàng chục giây). ĐÃ SỬA: chờ theo thời gian thật, vào thẳng máy chủ WebSocket khi chạy trên Cloudflare, chống gọi kiểm tra 2 lần song song.
- Thêm `tools/playtest.py` (giao tranh, mobile, online 2 người).

## Backlog
- Cân bằng độ khó đợt 1 (người chơi mới dễ hy sinh sớm): giảm độ chính xác địch ở xa, thêm báo hướng bị bắn rõ hơn.
- Thêm bản đồ thứ hai (rừng/đường hầm hẹp) và cách chọn bản đồ.
- Thêm lựu đạn (ném, nảy, nổ lan).
- Địch biết núp sau bao cát, ném lựu đạn khói.
- Chế độ online đồng đội (co-op) đánh bot cùng nhau.
- Bảng xếp hạng điểm chiến dịch.

## 2026-11-12 (tối)
- Nhân vật: vải quân phục có ánh vải (sheen), màu da khác nhau, mắt có lòng trắng, môi, gò má, cằm; bộ đội có ba lô con cóc + bi đông; lính Mỹ có quai mũ + dây đạn chéo; hoạt ảnh thở, giật súng, khựng khi trúng đạn, ngã gập gối; chớp lửa đầu nòng của địch/người chơi khác; bóng mờ dưới chân (tier low).
- Vỏ đạn đồng văng ra khi bắn (góc nhìn thứ nhất).
- Online: chat chữ (Enter/T, nút CHAT) qua presence; mic bộ đàm (giữ V, nút MIC) — μ-law 16kHz qua WebSocket nhị phân, chỉ chạy trên bản Cloudflare (claude.ai chặn micro).

## 2026-11-12 – v3.2
- Menu chọn trận đánh + nhiệm vụ (Giữ trận địa / Giải cứu con tin). Online chọn bản đồ theo phòng.
- NPC đồng đội (bộ đội) đi theo, tự tìm và bắn địch; địch chọn mục tiêu gần nhất (người chơi hoặc đồng đội).
- Lính gác có trạng thái cảnh giác: đứng canh, phát hiện theo góc nhìn/tiếng súng, báo động lan sang đồng bọn.
- Nhiệm vụ giải cứu: giữ E / nút GIỮ CỨU 1,6 giây để cởi trói, con tin đi theo, đưa về vòng xanh sơ tán; quân tiếp viện địch tới sau khi giải cứu; con tin hy sinh = thất bại. Có chỉ dẫn mục tiêu trên màn hình + minimap.
- Mobile: kiểm tra xoay màn hình liên tục, nút "Toàn màn hình + xoay ngang", "Vẫn chơi màn hình dọc", hướng dẫn cài PWA trên iPhone (manifest + icon), worker trả no-cache cho trang game, hiện số phiên bản ở menu.
