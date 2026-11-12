# Nhật ký đồ hoạ FIRELINE '68

## 2026-11-12 – v2 (nền tảng)
- Vật liệu PBR (albedo + normal + AO/roughness/metal) nướng bằng GPU cho: bê tông cốp pha, ván gỗ, nền đất đá, trần gỗ, bao cát, hòm đạn (stencil "ĐẠN 7,62"), vải quân phục, camo, kim loại súng, gỗ súng, sơn olive, da, da thuộc.
- Biến thiên vĩ mô theo toạ độ thế giới (chống lặp texture), vũng nước phản chiếu trên nền.
- Đèn bóng tròn có nón sáng thể tích giả, chập chờn; pool đèn động gán theo vị trí người chơi; bóng đổ từ đèn gần nhất (high: 1, ultra: 2).
- Hậu kỳ: MSAA x4 (HalfFloat), GTAO, Bloom, color grade "Realistic" (tham khảo phong cách Delta Force), CAS sharpen, vignette, film grain, chromatic aberration nhẹ.
- Dynamic resolution scaling giữ FPS; 4 mức chất lượng low/med/high/ultra.
- Nhân vật dựng lại bằng capsule: bộ đội (mũ cối + sao đỏ, dép cao su, khăn), lính Mỹ (M1 camo, áo giáp M69, giày lính); súng 3D chi tiết; tay có ngón trong góc nhìn thứ nhất; ngắm ADS.

## Backlog ý tưởng
- Decal máu/bụi trên tường, vết cháy sau nổ B40.
- Khói súng đọng lại trong không khí (volumetric fake), tàn lửa.
- Shell casing (vỏ đạn văng) có vật lý đơn giản.
- Hoạt ảnh nạp đạn chi tiết (tháo băng đạn).
- Screen-space reflections cho vũng nước (chỉ ultra).
- Biến thể tường: rễ cây, ống thông gió, dây điện võng giữa các đèn.
- Khuôn mặt nhân vật chi tiết hơn, hoạt ảnh chết theo ragdoll đơn giản.
- TAA / temporal upscaling cho mobile.

## 2026-11-12 – v3 bước 1: chất liệu chụp thật
- Thay chất liệu tự tạo bằng ảnh PBR quét từ vật thật của Poly Haven (CC0): tường bê tông `concrete_wall_006`, tường ván `wood_planks_dirt`, nền `dirt_floor`, trần `old_wood_floor`, cột/xà `rough_wood`, hòm đạn `green_rough_planks` (+ chữ stencil "ĐẠN 7,62" dạng decal), kim loại `green_metal_rust`. Mỗi bộ có diff + normal + ARM (AO/độ nhám/kim loại), 2K (tier med trở lên) và 1K (tier low).
- Phản chiếu môi trường bằng HDRI thật `boiler_room` (Poly Haven).
- Vẫn giữ chất liệu nướng GPU làm dự phòng nếu không tải được ảnh.
- Lính cầm súng đúng tư thế nhờ IK 2 khớp (trước đó dang tay chữ T).
- Tiếp theo: ánh sáng tính sẵn bằng Blender (baked GI), mô hình đồ vật thật, nhân vật có xương + hoạt ảnh.
