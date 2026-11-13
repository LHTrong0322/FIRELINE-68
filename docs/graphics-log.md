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

## 2026-11-12 – v3.2: bản đồ lịch sử, NPC, giải cứu con tin, tối ưu
- 3 bản đồ: Địa đạo Củ Chi 1968 (trong hầm), Đồi A1 – Điện Biên Phủ 1954 (đêm, giao thông hào, hầm gạch, hố bộc phá, pháo sáng), Tà Cơn – Khe Sanh 1968 (sương sớm, đất đỏ bazan, đường băng thép PSP, dây thép gai, boongke bao cát, pháo).
- Ánh sáng ngoài trời: trăng/mặt trời có bóng đổ, bầu trời sao, sương mù, rừng cây + đồi núi xa, đống lửa bập bùng, pháo sáng thả dù.
- Chất liệu thật thêm: excavated_soil_wall, red_brick, red_laterite_soil_stones, brown_mud_02, metal_grate_rusty, burned_ground_01.
- Phe địch theo lịch sử: quân viễn chinh Pháp (1954: MAS-36, MAT-49, mũ M1 trơn) và lính Mỹ (1968).
- Tối ưu: gộp mảnh nhân vật (mergeGeometries, ~4x ít draw call), chuột thô (unadjustedMovement), nội suy vị trí người chơi online, gửi trạng thái 20Hz.

## 2026-11-12 – v3.3
- Cỏ tranh instanced (2 thẻ chéo, alpha test) lay theo gió trong vertex shader; dày ở Khe Sanh, thưa/khô ở Đồi A1.
- Mưa đêm Điện Biên Phủ (line streaks theo camera) + bề mặt ướt (giảm độ nhám nền/hào/tường) phản chiếu lửa và pháo sáng + tiếng mưa.

## 2026-11-13 — Nhân vật dựng bằng Blender (v3.4)
- Kỹ thuật: thân người liền một khối có xương (skinned mesh) thay cho ghép khối rời; hoạt ảnh làm sẵn trong Blender (IK 2 khớp để hai tay bám súng), chơi bằng AnimationMixer + crossfade, cộng thêm góc ngắm (pitch) lên xương ngực theo thời gian thực — cách làm "animation layer" phổ biến ở các game FPS lớn.
- Tệp: `tools/blender/build_soldier.py` (chạy bằng `pip install bpy`) → `public/assets/models/soldier.glb` (~340KB, 7 hoạt ảnh: aim, walk, run, idle, walkFree, captive, death).
- Game: `loadSoldierGLB()` + `buildSoldierSK()`; mũ, mặt, trang bị, súng gắn vào xương bằng `boneAttach()`. Nếu tải GLB lỗi sẽ tự quay về mô hình cũ (`buildSoldierProc`).
- Bài học: IK có pole target trong Blender bị kẹt khi mục tiêu gần vai → bỏ pole, solver tự gập khuỷu ra ngoài và đạt đúng vị trí.
- Kiểm tra: check.py low/high ĐẠT, playtest ĐẠT, ảnh cận cảnh `tools/closeup.py`.
- Backlog: nướng ánh sáng (lightmap) bằng Blender; thêm ngón tay/khuôn mặt dựng bằng Blender; quân phục có nếp gấp (normal map riêng); hoạt ảnh nạp đạn, ném lựu đạn, cúi người.

## 2026-11-13 — Ánh sáng tính sẵn + bóng nắng theo người chơi (v4.0)
- `bakeLighting()`: mỗi lần dựng bản đồ tính một ảnh ánh sáng (4 điểm ảnh/ô lưới): độ che khuất góc tường (AO) và ánh sáng của mọi đèn/đống lửa có kiểm tra bị tường che. Shader `addMacro` cộng ánh sáng này vào tường/sàn/hào → đèn ở xa vẫn toả ánh ấm, góc tường tối tự nhiên (trước đây chỉ vài đèn gần nhất có ánh sáng).
- Bóng mặt trời giờ đi theo người chơi (`followSun`, khung 96 m, bám lưới 4 m để không rung) → bóng nét hơn trên bản đồ rộng.
- Trời hoàng hôn mới (Him Lam) với mặt trời thấp, bầu trời cam.
- Backlog: dựng lại khuôn mặt bằng Blender; nếp gấp quân phục; ánh sáng tính sẵn cho cả trần hầm và vật thể.

## 2026-11-13 — v4.1: đại tu nhân vật + biểu tượng bằng Blender
- **Nhân vật mới** (`tools/blender/build_soldier_mh.py`): thân người thật từ MakeHuman (CC0, kèm khung xương "game_engine" và trọng số da CC0 lấy từ repo makehumancommunity/mpfb2 — `tools/blender/mh/LICENSE.ASSETS.md`). Có khuôn mặt thật (Á cho bộ đội, Âu cho lính Mỹ/Pháp), mắt, tóc cắt ngắn, ngón tay nắm báng súng. Quân phục may thành lớp vỏ riêng phồng theo dáng người, có nếp gấp ở khuỷu tay, đầu gối, eo; quần túm ống; lính Mỹ có giày cao cổ, bộ đội đi dép. Hai file: `soldier_vn.glb`, `soldier_us.glb` (~0,9MB mỗi file, ~7–9k đỉnh).
- **Vải thật**: quân phục dùng ảnh chụp vải lanh (Poly Haven `rough_linen`, CC0), bao cát dùng vải bố (`hessian_230`).
- **Bao cát dựng từng bao** trong Blender (`build_sandbags.py`, `sandbags.glb`), xếp so le — thay khối hộp cũ (từ mức đồ hoạ Vừa).
- **Biểu tượng nút cảm ứng** dựng 3D và render bằng Cycles (`build_icons.py`): viên đạn, mũi tên nhảy, người nằm, băng đạn + chữ R, lựu đạn, bộc phá, hộp cứu thương, xe đẩy quân nhu, bàn tay, cửa thoát…
- **Chu kỳ ngày – đêm** ngoài trời: ngày 5 phút, đêm 1,5 phút, chuyển 25 giây; Đồi A1 bắt đầu ban đêm rồi sáng dần.
- **Nhận diện ta/địch**: mũi tên xanh trên đầu đồng đội, dấu đỏ trên địch đang lộ, chữ thập đỏ trên đồng đội gục; bộ đội mặc màu ô-liu sáng hơn lính Mỹ.
- Backlog: lính Pháp riêng (mũ, quân phục); biểu cảm khuôn mặt; vật thể khác bằng Blender (xe, lô cốt, cây cối); ảnh chụp da người.

## 2026-11-13 — v4.3 (phiên tương tác)
- Pháo: hố nổ (decal canvas), mảnh đất văng, lửa hãm nòng, rung camera theo khoảng cách; hiệu ứng chết (súng/mũ văng, bụi khi ngã).
- Hiệu năng: giới hạn FPS tuỳ chọn, bóng cập nhật thưa.
- Backlog đồ hoạ lớn: TAA + upscale, bake lightmap Blender theo từng map, heightmap địa hình thật, texture da/mặt chi tiết hơn, thử WebGPURenderer khi ổn định.

## 2026-11-13 — v4.6: bước nhảy bầu trời & khí quyển
- **Dọn kho:** xoá bộ ảnh `burnt` không dùng; nén lại toàn bộ ảnh chất liệu (diff q84 4:2:0, nor q86/arm q80 4:4:4, progressive) → thư mục ảnh 138MB → ~50MB, PSNR ~32–34dB.
- **Bầu trời HDRI thật (Poly Haven CC0):** `kloofendal_48d_partly_cloudy_puresky` (ngày), `kloppenheim_06_puresky` (hoàng hôn – Him Lam). Nền 4K (2K cho Thấp/Vừa) + HDR 1K làm ánh sáng môi trường; vị trí nắng khớp mặt trời trong ảnh. Shader trời tự hoà vào màu sương ở chân trời.
- **Phát hiện lỗi cũ:** camera.far=160 nên trời (bán kính 420) và núi xa (170–270m) chưa từng hiện. Ngoài trời giờ far=700.
- **Sương mù khí quyển theo độ cao** (kiểu Exponential Height Fog của Unreal/Frostbite) + tán xạ nắng về phía mặt trời, viết đè ShaderChunk fog dùng uniform chia sẻ.
- **Tia nắng (god rays)** hậu kỳ cho Cao/Siêu nhất: làm mờ toả tia từ vị trí mặt trời, trời có alpha=0 làm mặt nạ (tham khảo GPU Gems 3 ch.13 "Volumetric Light Scattering as a Post-Process").
- **Bóng mây trôi** trên mặt đất (Cao/Siêu nhất) và **biến thiên màu đất cỡ lớn** chống lặp vân (MACRO_VAR) cho nền, hào, đất ngoài bản đồ.
- **Đồi rừng xa** dạng vòm gợn tán cây thay cho hình nón.
- Test: check low/high ĐẠT, `tools/skytest.py` (mới) chụp khesanh/himlam.
- Backlog: thay tán cây "nấm" low-poly bằng cây GLB; súng góc nhìn thứ nhất dựng lại bằng Blender + vân gỗ/kim loại thật; da mặt nhân vật; TAA.

## 2026-11-13 — v4.7: "đại phẫu" nhân vật
- **Khuôn mặt:** thêm ~20 target chi tiết CC0 của MakeHuman (mpfb2, chép vào `tools/blender/mh/face/`): gò má, cằm, sống mũi, cánh mũi, mắt, lông mày, môi. Lính VN mặt Á Đông rõ (asian 1.0), lính Mỹ mặt vuông, cằm nhô.
- **Da vẽ bằng thuật toán** (`tools/blender/skintex.py`): rải màu theo toạ độ 3D lên lưới UV 2048: sắc da loang, má/mũi/tai hồng nhẹ, quầng mắt, môi, râu lún phún, lông mày vẽ hình học theo cung mắt, chân tóc mềm, kèm bản đồ pháp tuyến lỗ chân lông. Tông da VN sáng ấm (214,168,132) — sửa lỗi "da đen".
- **Mắt thật:** nhãn cầu tròn đều + ảnh mống mắt CC0 MakeHuman (brown_eye.png), VN nâu đen, Mỹ xanh xám; vật liệu bóng ướt.
- Trong game dùng ảnh da/mắt từ GLB, mỗi lính nhân hệ số sắc da nhẹ (`SKIN_MUL`). Cập nhật `SKM.vn` theo khung xương mới.
- Tán cây: khối lô nhô nhiều cụm thay khối 20 mặt; đồi xa lùi ra xa, thấp và sẫm hơn.
- Test: `tools/portrait.py` (mới), check low/high, playtest.
- Backlog: mũ cối/mũ sắt dựng Blender có vân vải/sơn thật; quân phục có đường may, túi, nếp nhăn bake; súng góc nhìn thứ nhất.
