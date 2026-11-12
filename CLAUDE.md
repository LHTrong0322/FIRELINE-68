# FIRELINE '68 – hướng dẫn cho bot tự cải tiến đồ hoạ

Game FPS 3D chạy trên trình duyệt (Three.js r160 từ CDN jsDelivr), deploy tự động lên Cloudflare Workers mỗi khi có commit vào `main`.

## Cấu trúc
- `public/index.html`: toàn bộ game trong một file (HTML + CSS + JS module). Vật liệu PBR được "nướng" bằng GPU (shader `SURF.*`), hậu kỳ gồm GTAO + Bloom + `FinalShader` (CAS sharpen, color grade).
- `worker/index.js`: máy chủ online (Durable Object relay WebSocket). Chỉ sửa khi thật cần.
- `tools/check.py <low|med|high|ultra>`: test tự động (wrangler dev + Chrome headless). Đạt = không lỗi JS và ảnh không đen/trắng toàn bộ. Ảnh chụp nằm ở `tools/shots/`, hãy MỞ RA XEM để tự đánh giá.
- `public/assets/tex/`: ảnh chất liệu chụp thật Poly Haven (CC0), `<key>_<1k|2k>_<diff|nor|arm>.jpg` + `env_1k.hdr`, nạp bởi `loadRealTextures()`. Có thể tải thêm từ api.polyhaven.com / dl.polyhaven.org / ambientcg.com (chỉ tài nguyên CC0, dùng curl kèm User-Agent). Giữ ảnh ≤2K, tổng thư mục assets < 150MB.
- `docs/graphics-log.md`: nhật ký các lần cải tiến. Luôn đọc trước khi làm và ghi thêm sau khi làm.

## Quy trình mỗi lần chạy (một cải tiến nhỏ, có kiểm chứng)
1. Đọc `docs/graphics-log.md` để biết đã làm gì và còn backlog gì.
2. Nghiên cứu 1 kỹ thuật đồ hoạ từ các game FPS hàng đầu (Delta Force, Call of Duty, Battlefield, Escape from Tarkov, Ready or Not, Counter-Strike 2…) qua bài phân tích công khai: GDC talk, Digital Foundry, blog kỹ thuật, tài liệu engine. Chỉ học KỸ THUẬT và phong cách. Tuyệt đối không tải/sao chép texture, model, âm thanh hay ảnh chụp của game khác.
3. Chọn MỘT cải tiến cụ thể, áp dụng được trong WebGL2/Three.js r160 (ví dụ: vật liệu chi tiết hơn, ánh sáng/bóng, hậu kỳ, hạt/khói, hoạt ảnh vũ khí, chi tiết môi trường, nhân vật). Ưu tiên tác động thị giác lớn nhưng rẻ cho hiệu năng.
4. Sửa `public/index.html`. Giữ hiệu năng tier `low` (mobile) không nặng hơn; tính năng nặng chỉ bật ở `high`/`ultra` qua bảng `QT`.
5. Chạy `python3 tools/check.py low` và `python3 tools/check.py high`. Mở ảnh trong `tools/shots/` để xem có đẹp hơn và không hỏng hình không.
6. Nếu ĐẠT cả hai và ảnh trông tốt hơn: commit thẳng vào `main` rồi push (Cloudflare tự deploy). Commit message tiếng Việt, mô tả ngắn cải tiến.
   Nếu KHÔNG ĐẠT: thử sửa tối đa 2 lần; vẫn hỏng thì `git checkout -- public/index.html`, push nhánh `bot/thu-nghiem-<ngày>` nếu đáng giữ, và ghi lý do vào log. KHÔNG BAO GIỜ push bản lỗi vào `main`.
7. Ghi vào `docs/graphics-log.md`: ngày, kỹ thuật, nguồn tham khảo (link), thay đổi, kết quả kiểm tra, ý tưởng tiếp theo cho backlog.

## Ràng buộc
- Chỉ được tải script từ cdn.jsdelivr.net/npm, cdnjs, unpkg (giới hạn CSP khi chạy trong claude.ai). Không fetch tài nguyên ngoài khác.
- Không thêm nội dung bạo lực máu me quá mức. Giữ chủ đề: bộ đội Việt Nam giữ căn cứ ngầm, bot là lính Mỹ (1968).
- Không phá chế độ online (`net`, `wsRoom`, `worker/`), điều khiển cảm ứng, xoay ngang.
- Giữ dòng credit "Agent build by @Trong0322".

---
# Bot trợ lý QA: sửa lỗi & nâng cấp trò chơi

Bot thứ hai (chạy riêng với bot đồ hoạ) chuyên ổn định game và nâng cấp lối chơi. Nhật ký: `docs/dev-log.md`.

## Quy trình mỗi lần chạy
1. Đọc `docs/dev-log.md` (lỗi đã biết, backlog) và `git log -15` để biết bot đồ hoạ vừa đổi gì.
2. Chạy `python3 tools/playtest.py`: chiến dịch có giao tranh thật, điện thoại xoay ngang (cảm ứng), 2 người chơi online. Kèm `python3 tools/check.py low`.
3. MỞ TỪNG ẢNH `tools/shots/playtest_*.png` và soi kỹ: đốm đen/trắng lạ, vật thể nhấp nháy hoặc mất, UI chồng chéo, chữ bị che, súng lệch, màn hình quá tối hoặc quá sáng, nhân vật biến dạng.
4. Ưu tiên SỬA LỖI theo thứ tự: crash/lỗi JS → hỏng hình → online → cảm ứng/mobile → cân bằng gameplay → hiệu năng.
5. Nếu không có lỗi: làm MỘT nâng cấp lối chơi nhỏ từ backlog (ví dụ: bản đồ mới, loại địch mới, vũ khí mới, chế độ chơi, hoạt ảnh, âm thanh, HUD, cân bằng độ khó, nhiệm vụ trong trận).
6. Chạy lại `tools/playtest.py` và `tools/check.py low` + `high`. Chỉ khi ĐẠT hết mới commit vào `main` và push (Cloudflare tự deploy). Không đạt sau 2 lần sửa thì hoàn tác, không bao giờ push bản lỗi.
7. Ghi `docs/dev-log.md`: ngày, lỗi tìm thấy (kèm cách tái hiện), cách sửa, nâng cấp đã làm, kết quả test, backlog mới.

## Lưu ý kỹ thuật
- Từ v4.0: chế độ `base` (bản đồ nới rộng bằng `baseGrid()`, xe chỉ huy `hqs`), `bunker` (bản đồ có `bunker:true`, điểm `1 2 3`), `rescue`. Kiểm tra thêm bằng `python3 tools/featuretest.py` và `tools/modetest.py`. Test chờ theo `state.time` (thời gian trong game) vì SwiftShader rất chậm.
- Sảnh online: worker trả danh sách phòng ở `/rooms` (Durable Object tên `__lobby__`). Đừng phá.
- Môi trường test dùng SwiftShader (CPU), FPS rất thấp: hoạt ảnh theo thời gian có thể chưa xong khi chụp. Đừng nhầm với lỗi.
- Card đồ hoạ thật dùng bộ đệm HalfFloat: mọi giá trị sáng > 65504 thành vô cực và gây đốm đen sau bloom. Đã có `SanitizeShader`, đừng gỡ.
- Hạt (`Particles`) dùng màu RGBA, độ mờ nằm ở kênh alpha. Đừng đổi lại kiểu làm tối dần màu (từng gây lỗi chấm đen).
