# FIRELINE '68 – hướng dẫn cho bot tự cải tiến đồ hoạ

Game FPS 3D chạy trên trình duyệt (Three.js r160 từ CDN jsDelivr), deploy tự động lên Cloudflare Workers mỗi khi có commit vào `main`.

## Cấu trúc
- `public/index.html`: toàn bộ game trong một file (HTML + CSS + JS module). Vật liệu PBR được "nướng" bằng GPU (shader `SURF.*`), hậu kỳ gồm GTAO + Bloom + `FinalShader` (CAS sharpen, color grade).
- `worker/index.js`: máy chủ online (Durable Object relay WebSocket). Chỉ sửa khi thật cần.
- `tools/check.py <low|med|high|ultra>`: test tự động (wrangler dev + Chrome headless). Đạt = không lỗi JS và ảnh không đen/trắng toàn bộ. Ảnh chụp nằm ở `tools/shots/`, hãy MỞ RA XEM để tự đánh giá.
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
