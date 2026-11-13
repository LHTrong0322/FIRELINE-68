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

## 2026-11-13 — v4.1
- Sửa: nút rời pháo (trước đây giữ E bị chiếm lại ngay) → nút RỜI PHÁO riêng + khoá 1,6s; bản đồ nã pháo xa (chọn điểm, đạn bay vòng cầu, không hiện địch).
- Bỏ tạm dừng: nút cửa ở góc mở MENU (Tiếp tục / Cài đặt / Rời trận hoặc Rời phòng), trận vẫn chạy. Quân nhu cũng không dừng trận.
- Chat điện thoại có nút ✕ đóng và ➤ gửi.
- Sảnh online kiểu thẻ phòng (ảnh bản đồ, tên, số người), nút TẠO PHÒNG mở hộp chọn bản đồ có ảnh. Worker báo danh phòng 45 giây/lần, phòng im 2 phút tự biến mất (sửa phòng "không thoát được" vẫn hiện trong danh sách).
- Mỗi bên 8 người (người chơi + 7 đồng đội; địch 8). Thanh máu XE TA / XE ĐỊCH có %, thanh nhiệm vụ ghi khoảng cách tới căn cứ địch, bản đồ nhỏ tô vùng căn cứ và xe chỉ huy màu đỏ.
- Tiếp tế có băng rôn lớn giữa màn hình + dấu ✈/▣ chỉ vị trí gói.
- Nút cứu nhỏ lại, cờ chữ thập đỏ cắm cạnh đồng đội khi cứu. Nút đổi súng hiện hình súng kế tiếp.
- Ảnh đại diện bản đồ: `tools/thumbs.py` → `public/assets/maps/*.jpg`.

## 2026-11-13 — v4.2
- Bắn pháo kiểu thật: lửa đầu nòng kéo dài loé ngắn, sóng bụi mặt đất, nòng giật lùi rồi về, khói tỏa sau bắn, đạn có vệt sáng + khói, tiếng nổ trầm vang dài, tiếng rít khi đạn rơi, nổ có loé trắng + cột đất + vòng sóng xung kích. Camera bám theo đạn của người chơi, chậm lại lúc gần chạm đất (chạm/E để bỏ qua). Test: `tools/arttest.py`.
- Bố cục cảm ứng gọn: nút phụ (bộc phá, cứu thương, đèn, quân nhu) gom vào BA LÔ; nút NGỒI giữ 0,4s = nằm bò; đổi súng + menu lên góc trên; số đạn xuống giữa đáy màn hình. Sửa nút quân nhu đè nút R.
- Mặc định đồ hoạ Siêu (khoá lưu mới `quality3`); Siêu giảm bộ nhớ (nướng chất liệu 1024px thay 2048px — bản cũ có thể hết bộ nhớ GPU nên không vào được game), mất ngữ cảnh WebGL thì tự hạ một bậc và tải lại; 20 giây đầu dưới 22 FPS thì lần sau tự hạ.
- Bản đồ to hơn 20% (CELL 3,6m), lính cao hơn (~1,8m), tầm mắt người chơi 1,66m, hộp trúng đạn khớp chiều cao mới.
- Cây cọ, dương xỉ, bụi cây, đá từ mô hình chụp thật Poly Haven (CC0, đã giảm đa giác trong Blender — `tools/blender/build_vegetation.py`).
- Trận tối thiểu 5 phút: xe chỉ huy 6000 máu và được "gia cố" (không xuống dưới 15%) trong 5 phút đầu; lô cốt 2 mở sau 100 giây, lô cốt 3 sau 200 giây, chiếm mất 18 giây.
- Chữ "XE ĐỊCH" nhỏ, mờ, nằm cao hơn và gần như trong suốt khi ở gần tâm ngắm (không che địch). Chữ tiếp tế nhỏ lại.
- Chế độ con tin: chưa tái hiện được lỗi cụ thể (bắt đầu, quỳ, giải cứu đều chạy); đã sửa đồng đội xuất hiện chồng lên người chơi.
- Bot cố vấn mới (lịch hằng ngày 17:19): chỉ review và ghi `docs/advisor/YYYY-MM-DD.md`, không sửa code.

## 2026-11-13 — v4.3 (theo yêu cầu người chơi)
- Nút quân nhu chuyển xuống dưới nút bắn (nhỏ 40px), bỏ khỏi menu trang bị → không đè nút R nữa.
- Thông báo hạ gục: biểu tượng bật lên giữa màn hình, âm "kill", chuỗi HẠ 2–4 LIÊN TIẾP / HUỶ DIỆT!, bắn đầu có chữ riêng, nhắc nhặt tiền.
- Hiệu ứng địch chết: súng văng khỏi tay, mũ văng khi bắn đầu, bụi + tiếng khi xác chạm đất.
- Pháo chân thật: nòng xoay có giới hạn tốc độ (0,55/0,35 rad/s), đạn bay theo hướng nòng, nạp đạn 3,2s có vỏ đạn văng, bắn từ bản đồ thì xếp lệnh chờ nòng xoay xong; lửa hai bên hãm nòng; tiếng nổ xa đến trễ theo khoảng cách; hố đạn trên đất; đất đá văng; rung máy theo khoảng cách.
- Giảm nóng máy/mượt hơn: cài đặt Khung hình 60/45/30 (điện thoại mặc định 45), bóng cập nhật thưa hơn, độ phân giải động theo mức khung hình, dấu đơn vị cập nhật cách khung.
- Test: arttest high ĐẠT, check low/high ĐẠT, ảnh điện thoại kiểm tra bố cục nút.

## 2026-11-13 — v4.4
- Nút Ba lô chuyển xuống cạnh nút Quân nhu (dưới nút bắn, 38px); menu ba lô mở sang trái nút bắn, không che nút bắn.
- Mặc định khi vào game: đồ hoạ Cao + 60 khung hình (khoá lưu mới `tl_quality4`/`fps4` để người cũ đang Siêu nhất cũng về Cao). Điện thoại ở mức Cao dùng mật độ điểm ảnh 1.4 cho mượt.
- Test: check low/high ĐẠT, ảnh điện thoại kiểm tra bố cục.

## 2026-11-13 — v4.5
- Thêm chế độ Khung hình "Tự động" (mặc định, khoá `fps5`): máy tính 60, điện thoại 45; pin <30% không sạc hoặc máy đuối (độ phân giải động đã xuống đáy mà vẫn chậm 3 lần liên tiếp) thì hạ 30 cho mát và đều khung hình. Hàm `fpsCap()`.
- Test: check low/high ĐẠT.
