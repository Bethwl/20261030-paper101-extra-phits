"""Parser riêng cho 2026.10.30_Paper10.1_extra_PHITS (run.parser: custom).

Đọc các file tally PHITS của từng subproject, trả về 1 dòng giá trị THÔ (chưa tính đại lượng vật lý).
Luật GOAT: đọc lỗi/thiếu file/thiếu khối => ném exception (job FAILED, được chạy lại). Số 0 do PHITS
ghi ra là 0 thật (vd vỏ cầu SAFE quá sâu ở năng lượng thấp) và được giữ nguyên.

Khối dữ liệu tally PHITS: dòng tiêu đề '#  num ...' rồi các dòng số; cột cuối = sai số tương đối,
cột kế cuối = giá trị. Mesh reg: [num, reg, volume, value, r.err]; T-Cross reg: [num, area, value, r.err].
Tally có multiplier ghi mỗi mset thành 1 khối riêng theo thứ tự mset1, mset2, ...
"""

from pathlib import Path

SAFE_D = ["0p1", "0p3", "0p5", "0p8", "1", "1p5", "2"]


def _blocks(path: Path) -> list:
    blocks, cur = [], None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("#") and s[1:].split()[:1] == ["num"]:
            cur = []
            blocks.append(cur)
            continue
        if cur is None:
            continue
        if not s:
            cur = None
            continue
        try:
            cur.append([float(x) for x in s.split()])
        except ValueError:
            cur = None
    return [b for b in blocks if b]


def _file(workdir: Path, prefix: str, job: dict) -> Path:
    p = Path(workdir) / f"{prefix}_{job['job']}.out"
    if not p.is_file() or p.stat().st_size == 0:
        raise FileNotFoundError(f"thiếu file tally {p.name}")
    return p


def _need(blocks: list, n: int, name: str) -> list:
    if len(blocks) < n:
        raise ValueError(f"{name}: cần {n} khối dữ liệu, chỉ thấy {len(blocks)}")
    return blocks


def _put(row: dict, key: str, r: list):
    row[key] = r[-2]
    row[f"{key}_rel_err"] = r[-1]


def parse(workdir, job: dict) -> list:
    sub = job["subproject"]
    row = {}
    if sub == "IFRAC":
        b = _need(_blocks(_file(workdir, "rate", job)), 5, "rate")
        for key, blk in zip(("compton", "rayleigh", "photoelec", "pair", "total"), b):
            _put(row, key, blk[0])
        row["volume_cm3"] = b[0][0][2]
    elif sub == "KA":
        dep = _need(_blocks(_file(workdir, "dep", job)), 1, "dep")[0]
        by_reg = {int(r[1]): r for r in dep}
        if 100 not in by_reg or 101 not in by_reg:
            raise ValueError("dep: thiếu region 100 (không khí) hoặc 101 (mẫu)")
        _put(row, "dep_air_MeV", by_reg[100])
        _put(row, "dep_sample_MeV", by_reg[101])
        k = _need(_blocks(_file(workdir, "kerma", job)), 2, "kerma")
        _put(row, "kerma_lib_air", k[0][0])
        _put(row, "kerma_lib_sample", k[1][0])
    elif sub == "SAFE":
        dep = _need(_blocks(_file(workdir, "dep", job)), 1, "dep")[0]
        if len(dep) != len(SAFE_D):
            raise ValueError(f"dep: cần {len(SAFE_D)} vỏ cầu, thấy {len(dep)}")
        for d, r in zip(SAFE_D, dep):
            _put(row, f"dep_d{d}cm_MeV", r)
    elif sub in ("SR", "THN"):
        _put(row, "uncollided_flux", _need(_blocks(_file(workdir, "unc", job)), 1, "unc")[0][0])
        _put(row, "escaped_current", _need(_blocks(_file(workdir, "esc", job)), 1, "esc")[0][0])
        if job["sample"] != "BLANK":
            x = _need(_blocks(_file(workdir, "xs", job)), 3, "xs")
            for key, blk in zip(("lib_total", "lib_absorption", "lib_elastic"), x):
                _put(row, key, blk[0])
    else:
        raise ValueError(f"subproject lạ: {sub}")
    return [row]
