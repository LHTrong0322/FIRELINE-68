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

## 2026-11-12 – v3.3
- LỖI: nút giải cứu trên điện thoại không hoạt động (nút chưa gắn sự kiện chạm, `touch.use` không bao giờ bật). ĐÃ SỬA: giữ nút ổ khoá to ở giữa màn hình, có vòng tiến trình.
- Toàn bộ nút cảm ứng đổi sang biểu tượng hình (đạn, ống ngắm, mũi tên lên/xuống, băng đạn, đổi súng, đèn pin, ổ khoá, chat, mic).
- Đồng đội nâng lên 1 tiểu đội: người chơi + 8 chiến sĩ (tier low: 5), đội hình 2 hàng dọc; tăng quân địch tương ứng.

## 2026-11-13
- Sửa test: `tools/playtest.py` bước mobile bấm "CHIẾN DỊCH" giờ mở bảng chọn bản đồ → thêm bấm `#mStart` (trước đó treo chờ nút #bFire không hiện).
- Thêm `tools/closeup.py` chụp cận cảnh lính để soi hoạt ảnh.

## 2026-11-13 — v4.0: đại cập nhật lối chơi
- **Chế độ Công phá căn cứ** (thay chế độ giữ trận địa): bản đồ nới rộng 30→50 cột (`baseGrid()` tự thêm căn cứ 2 bên), mỗi bên 1 xe chỉ huy làm "trụ" (ta: xe tải, địch: xe thiết giáp, 4000 máu). Mất xe trước là thua. Hồi sinh 8 giây cho người chơi, đồng đội và địch.
- **Chiếm lô cốt** (2 bản đồ mới Him Lam 1954, Cồn Tiên 1967 — sinh bằng `/tmp/gen/bunker.py`, đã kiểm tra liên thông): chiếm lần lượt 3 điểm (vòng vàng, 12 giây), quân tiếp viện có hạn.
- **Tiền VNĐ**: hạ địch → xác có đốm vàng, phải tới nhặt. **QUÂN NHU** (B / nút giỏ hàng): chi viện chiến sĩ, hộp cứu thương, đạn, áo giáp, lựu đạn, bộc phá, trung liên RPD (vũ khí số 5).
- **Cứu đồng đội**: đồng đội gục 14 giây, giữ E + 1 hộp cứu thương để cứu. Hệ tương tác chung `updateInteract()` (con tin / đồng đội / pháo).
- **Kẽm gai** gây 5 máu mỗi 0,35s khi đi đứng; **nằm/bò** (Z), nhảy qua thì an toàn. **Lựu đạn** (G, bot cũng ném), **bộc phá** (X, phá xe mạnh). **Chiếm pháo** (giữ E cạnh pháo), bot cũng làm xạ thủ.
- **Máy bay tiếp tế** mỗi 2 phút (gói đỏ ta/xanh địch): chạm trước được, nhảy dậm lên gói địch để phá; bot cũng tranh gói.
- **Bot chia vai**: theo người chơi / tấn công / giữ nhà / đi tuần / săn người chơi / giữ-chiếm lô cốt / xạ thủ pháo; dùng `flowTo()` (đường đi tới điểm bất kỳ, tránh kẽm gai).
- **Bảng điểm** cờ VN – Mỹ/Pháp + thanh máu 2 xe chỉ huy.
- **Online**: worker có sảnh `/rooms`; tạo phòng là hiện trong danh sách, người khác bấm vào chơi cùng không cần nhập mã.
- **Đồ hoạ**: ánh sáng tính sẵn `bakeLighting()` (AO góc tường + ánh đèn/lửa xa có che khuất), bóng mặt trời đi theo người chơi, trời hoàng hôn cho Him Lam.
- Test mới: `tools/modetest.py` (các chế độ), `tools/featuretest.py` (nhặt tiền, cứu đồng đội, bộc phá, pháo, tiếp tế, hồi sinh, chiếm lô cốt — chờ theo thời gian trong game vì SwiftShader chậm). playtest online giờ kiểm tra danh sách phòng.
- Backlog: lính địch cũng nằm/bò; chỉ huy đồng đội bằng lệnh nhanh; xe chỉ huy di chuyển được; bản đồ chiếm lô cốt phe Mỹ phòng thủ trên đồi cao (có độ dốc); chế độ online đồng đội 2 phe.
