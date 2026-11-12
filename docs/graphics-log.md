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
