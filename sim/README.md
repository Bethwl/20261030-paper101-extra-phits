# sim/ — input PHITS cho các đại lượng ngoài MAC của Paper 10.1

Sinh tự động ngày 2026-10-30. Thành phần khối lượng S1–S8 lấy từ input MAC đã chạy
(`2026.10.30_Paper10.1_iso-1e8_PHITS`); bề dày lá mỏng chọn từ `theory/mac_theory.csv` (photon) và tiết diện
nơtron nhiệt nguyên tố Sears 1992 (chỉ để chọn bề dày). Số hạt ghi cứng trong `maxcas` của từng input
(không dùng `@PRIMARIES@`).

| Subproject | Job | Hạt | Hình học | Tally → cột CSV |
|---|---|---|---|---|
| IFRAC | 8 mẫu × 23 E | 1e6 | chùm bút chì photon, lá mẫu μx = 0.01 | T-Track × multiplier MT −1/−2/−3/−4/−5 → `compton, rayleigh, photoelec, pair, total` |
| KA | 8 × 23 | 1e7 | không khí 10 cm (ρ 0.001205) rồi lá mẫu μx = 0.005 | T-Deposit → `dep_air_MeV, dep_sample_MeV`; kerma thư viện (MT −5 × −6) → `kerma_lib_air, kerma_lib_sample` |
| SAFE | 8 × 23 | 1e7 | nguồn điểm 4π tâm cầu mẫu R = 30 cm | T-Deposit vỏ cầu [d±0.025] cm, d = 0.1…2 → `dep_d<d>cm_MeV` |
| SR | 8 × 4 bề dày (1/2/4/6 cm) × 7 E (1–14 MeV) + 7 BLANK | 1e6 | chùm bút chì nơtron; đĩa đếm r = 0.05 cm ở z = 100 | `uncollided_flux` (I; I0 = BLANK), `escaped_current`, σ thư viện `lib_total/absorption/elastic` |
| THN | 8 × 3 bề dày (Σt·x ≈ 0.05/0.1/0.2) + 1 BLANK | 1e6 | như SR, E = 0.0253 eV | như SR; phần hấp thụ = 1 − `escaped_current` |

Ghi chú vật lý:
- `uncollided_flux` là chùm hẹp thật (hạt tán xạ gần như không thể chạm đĩa 0.05 cm ở 100 cm) → Σt = ln(I0/I)/x.
  Σ_R (removal) của bài báo là đại lượng thực nghiệm khác, cỡ 2/3 Σt nơtron nhanh.
- Multiplier MT (photon −1 Compton, −2 Rayleigh, −3 quang điện, −4 tạo cặp, −5 tổng, −6 năng lượng/va chạm;
  nơtron −1 tổng, −2 hấp thụ, −3 đàn hồi) cho tiết diện trên mỗi nguyên tử trung bình của vật liệu — dùng dạng tỉ số.
- SAFE ở năng lượng thấp + vỏ sâu có thể ra 0 thật (vd S8 15 keV: 0.1 cm ≈ 14 mfp) — giữ nguyên 0, không bịa số.
- EGS5 (`negs=1`, cần cho [T-Interact]) crash ở bản PHITS 3.36 trên cả Windows lẫn Linux nên không dùng.
- Vật liệu nơtron dùng ký hiệu nguyên tố (PHITS tự tách đồng vị tự nhiên); cần `extra_packages: [phits_neu]`.
