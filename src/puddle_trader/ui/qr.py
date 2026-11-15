"""QR 코드 만들기 (추가 설치 없이). 휴대폰 카메라로 찍어 화면을 열 때 쓴다.

지원 범위는 필요한 만큼만: 바이트 모드, 오류 복원 수준 M, 버전 1~10 (최대 213바이트).
접속 주소 하나를 담기에는 버전 3~4 면 충분하다.
"""
from __future__ import annotations

from functools import lru_cache

# 버전별 (오류 복원 코드워드 수/블록, [(블록 수, 블록당 데이터 코드워드 수), ...]) — 수준 M
_BLOCKS = {
    1: (10, [(1, 16)]), 2: (16, [(1, 28)]), 3: (26, [(1, 44)]), 4: (18, [(2, 32)]),
    5: (24, [(2, 43)]), 6: (16, [(4, 27)]), 7: (18, [(4, 31)]), 8: (22, [(2, 38), (2, 39)]),
    9: (22, [(3, 36), (2, 37)]), 10: (26, [(4, 43), (1, 44)]),
}
_ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38],
          8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}
_MASKS = [
    lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0,
    lambda x, y: (x + y) % 3 == 0, lambda x, y: (x // 3 + y // 2) % 2 == 0,
    lambda x, y: x * y % 2 + x * y % 3 == 0, lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
    lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
]


# ---- 리드-솔로몬 (GF(256), 원시 다항식 0x11D) ------------------------------------
def _gf_mul(a: int, b: int) -> int:
    out = 0
    for i in range(7, -1, -1):
        out = (out << 1) ^ ((out >> 7) * 0x11D)
        out ^= ((b >> i) & 1) * a
    return out


def _rs_divisor(degree: int) -> list[int]:
    poly = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for j in range(degree):
            poly[j] = _gf_mul(poly[j], root)
            if j + 1 < degree:
                poly[j] ^= poly[j + 1]
        root = _gf_mul(root, 2)
    return poly


def _rs_remainder(data: list[int], divisor: list[int]) -> list[int]:
    rem = [0] * len(divisor)
    for byte in data:
        factor = byte ^ rem.pop(0)
        rem.append(0)
        rem = [r ^ _gf_mul(d, factor) for r, d in zip(rem, divisor, strict=True)]
    return rem


# ---- 데이터 → 코드워드 ---------------------------------------------------------
def _capacity(version: int) -> int:
    data_cw = sum(n * size for n, size in _BLOCKS[version][1])
    return data_cw - (2 if version < 10 else 3)      # 모드 4비트 + 글자 수 8/16비트


def _codewords(data: bytes, version: int) -> list[int]:
    ec_len, groups = _BLOCKS[version]
    total_data = sum(n * size for n, size in groups)
    bits: list[int] = [0, 1, 0, 0]                                   # 바이트 모드
    count_bits = 8 if version < 10 else 16
    bits += [(len(data) >> i) & 1 for i in range(count_bits - 1, -1, -1)]
    for byte in data:
        bits += [(byte >> i) & 1 for i in range(7, -1, -1)]
    bits += [0] * min(4, total_data * 8 - len(bits))                 # 종료 표시
    bits += [0] * (-len(bits) % 8)
    words = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = (0xEC, 0x11)
    words += [pad[i % 2] for i in range(total_data - len(words))]

    divisor = _rs_divisor(ec_len)
    blocks, pos = [], 0
    for n, size in groups:
        for _ in range(n):
            block = words[pos:pos + size]
            pos += size
            blocks.append((block, _rs_remainder(block, divisor)))
    out: list[int] = []
    for i in range(max(len(b) for b, _ in blocks)):                  # 데이터를 블록마다 번갈아
        out += [b[i] for b, _ in blocks if i < len(b)]
    for i in range(ec_len):                                          # 그다음 오류 복원 코드워드
        out += [e[i] for _, e in blocks]
    return out


# ---- 무늬 그리기 ---------------------------------------------------------------
class _Grid:
    def __init__(self, version: int):
        self.version = version
        self.size = size = version * 4 + 17
        self.dark = [[False] * size for _ in range(size)]
        self.fixed = [[False] * size for _ in range(size)]    # 기능 무늬(데이터가 못 들어가는 칸)

    def put(self, x: int, y: int, dark: bool) -> None:
        self.dark[y][x] = bool(dark)
        self.fixed[y][x] = True

    def function_patterns(self) -> None:
        size = self.size
        for i in range(size):                                        # 타이밍 무늬
            self.put(6, i, i % 2 == 0)
            self.put(i, 6, i % 2 == 0)
        for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):        # 위치 찾기 무늬 + 여백
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < size and 0 <= y < size:
                        self.put(x, y, max(abs(dx), abs(dy)) not in (2, 4))
        pos = _ALIGN[self.version]
        last = len(pos) - 1
        for i, cx in enumerate(pos):                                 # 정렬 무늬
            for j, cy in enumerate(pos):
                if (i, j) in ((0, 0), (0, last), (last, 0)):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        self.put(cx + dx, cy + dy, max(abs(dx), abs(dy)) != 1)
        self.format_bits(0)                                          # 자리만 먼저 잡아 둔다
        self.version_bits()

    def format_bits(self, mask: int) -> None:
        data = mask                                                  # 수준 M 의 표시 비트는 00
        rem = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits = ((data << 10) | rem) ^ 0x5412
        bit = lambda i: (bits >> i) & 1 == 1  # noqa: E731
        size = self.size
        for i in range(6):
            self.put(8, i, bit(i))
        self.put(8, 7, bit(6))
        self.put(8, 8, bit(7))
        self.put(7, 8, bit(8))
        for i in range(9, 15):
            self.put(14 - i, 8, bit(i))
        for i in range(8):
            self.put(size - 1 - i, 8, bit(i))
        for i in range(8, 15):
            self.put(8, size - 15 + i, bit(i))
        self.put(8, size - 8, True)                                  # 항상 검은 칸

    def version_bits(self) -> None:
        if self.version < 7:
            return
        rem = self.version
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        bits = (self.version << 12) | rem
        for i in range(18):
            a, b = self.size - 11 + i % 3, i // 3
            dark = (bits >> i) & 1 == 1
            self.put(a, b, dark)
            self.put(b, a, dark)

    def place(self, words: list[int]) -> None:
        """오른쪽 아래에서 시작해 두 칸 폭으로 지그재그로 올라가며 채운다."""
        size, i, total = self.size, 0, len(words) * 8
        for start in range(size - 1, 0, -2):
            right = start - 1 if start <= 6 else start               # 타이밍 무늬 열은 건너뛴다
            for vert in range(size):
                for j in range(2):
                    x = right - j
                    upward = (right + 1) & 2 == 0
                    y = size - 1 - vert if upward else vert
                    if not self.fixed[y][x] and i < total:
                        self.dark[y][x] = (words[i >> 3] >> (7 - (i & 7))) & 1 == 1
                        i += 1

    def apply_mask(self, mask: int) -> None:
        fn = _MASKS[mask]
        for y in range(self.size):
            for x in range(self.size):
                if not self.fixed[y][x] and fn(x, y):
                    self.dark[y][x] = not self.dark[y][x]

    def penalty(self) -> int:
        """읽기 어려운 모양(긴 줄, 큰 덩어리, 찾기 무늬 닮은꼴, 한쪽으로 쏠린 색)에 벌점."""
        size, rows = self.size, self.dark
        cols = [[rows[y][x] for y in range(size)] for x in range(size)]
        score = 0
        for line in rows + cols:
            run = 1
            for i in range(1, size):
                if line[i] == line[i - 1]:
                    run += 1
                    if run == 5:
                        score += 3
                    elif run > 5:
                        score += 1
                else:
                    run = 1
            text = "".join("1" if v else "0" for v in line)
            for pattern in ("10111010000", "00001011101"):
                start = text.find(pattern)
                while start != -1:
                    score += 40
                    start = text.find(pattern, start + 1)
        for y in range(size - 1):
            for x in range(size - 1):
                if rows[y][x] == rows[y][x + 1] == rows[y + 1][x] == rows[y + 1][x + 1]:
                    score += 3
        dark = sum(sum(r) for r in rows)
        return score + abs(dark * 20 - size * size * 10) // (size * size) * 10


# ---- 공개 함수 -----------------------------------------------------------------
@lru_cache(maxsize=16)
def matrix(text: str, mask: int | None = None) -> tuple[str, ...]:
    """QR 코드의 칸들. 줄마다 '1'(검은 칸)·'0'(흰 칸) 문자열. 너무 길면 ValueError."""
    data = text.encode("utf-8")
    version = next((v for v in sorted(_BLOCKS) if len(data) <= _capacity(v)), None)
    if version is None:
        raise ValueError("QR 코드에 담기에는 너무 길어요")
    words = _codewords(data, version)
    best: tuple[int, list[list[bool]]] | None = None
    for m in range(8) if mask is None else [mask]:
        grid = _Grid(version)
        grid.function_patterns()
        grid.place(words)
        grid.apply_mask(m)
        grid.format_bits(m)
        score = grid.penalty()
        if best is None or score < best[0]:
            best = (score, grid.dark)
    assert best is not None
    return tuple("".join("1" if v else "0" for v in row) for row in best[1])


def to_terminal(rows: tuple[str, ...] | list[str], quiet: int = 2) -> str:
    """터미널용 그림. 글자 한 칸에 QR 두 줄을 담고, 배경색을 직접 지정한다 (어두운 터미널 대비)."""
    size = len(rows)
    blank = "0" * (size + 2 * quiet)
    grid = [blank] * quiet + ["0" * quiet + r + "0" * quiet for r in rows] + [blank] * quiet
    if len(grid) % 2:
        grid.append(blank)
    chars = {("0", "0"): " ", ("1", "0"): "▀", ("0", "1"): "▄", ("1", "1"): "█"}
    lines = []
    for y in range(0, len(grid), 2):
        body = "".join(chars[(a, b)] for a, b in zip(grid[y], grid[y + 1], strict=True))
        lines.append(f"\033[30;107m{body}\033[0m")                   # 검은 글자, 밝은 흰 배경
    return "\n".join(lines)
