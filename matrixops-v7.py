"""
MatrixOps — Matrix Calculator
- Window title "MatrixOps — Matrix Calculator" with "Matrix Calculator" heading and the 6 operations listed below
- Strictly 6 operations with clear names:
  Addition, Subtraction, Multiplication, Transpose, Determinant, Inverse
- Dynamic rows & columns (1x1 up to 10x10) with smooth horizontal & vertical
  scrolling and auto-expanding input/result boxes when typing longer numbers
- Vertical web-style page flow: Matrices on top -> Operations -> Result -> Calculation Steps
Run: python matrixops.py
"""
import math
import tkinter as tk
from tkinter import messagebox


BG_PAGE = "#F8FAFC"
BG_CARD = "#FFFFFF"
BG_SUBTLE = "#F1F5F9"
BG_CELL_ACTIVE = "#EFF6FF"
BORDER_CARD = "#E2E8F0"
BORDER_CELL = "#CBD5E1"
BORDER_ACTIVE = "#2563EB"

TEXT_PRIMARY = "#0F172A"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#64748B"

ACCENT_PRIMARY = "#1D4ED8"
ACCENT_TEXT = "#FFFFFF"

SCROLL_TRACK = "#E2E8F0"
SCROLL_THUMB = "#94A3B8"
SCROLL_THUMB_HOVER = "#64748B"

MAX_DIM = 10
MIN_CELL_W = 5
MAX_CELL_W = 14
EPSILON = 1e-12


class MatrixError(ValueError):
    """Raised for invalid matrix data or mathematically invalid operations."""


def fmt(x):
    if abs(x) < 1e-10:
        return "0"
    if abs(x - round(x)) < 1e-10:
        return str(int(round(x)))
    return f"{x:.6g}"


def matrix_text(M):
    formatted = [[fmt(float(v)) for v in row] for row in M]
    widths = [max(len(row[j]) for row in formatted) for j in range(len(formatted[0]))]
    lines = []
    for row in formatted:
        lines.append("  [ " + "   ".join(val.rjust(widths[j]) for j, val in enumerate(row)) + " ]")
    return "\n".join(lines)


def op_addition(A, B, trace):
    ra, ca = len(A), len(A[0])
    rb, cb = len(B), len(B[0])
    if (ra, ca) != (rb, cb):
        raise MatrixError(f"Addition requires equal dimensions (Matrix A is {ra}x{ca}, Matrix B is {rb}x{cb}).")
    trace.append("OPERATION   :  Addition (Matrix A + Matrix B)")
    trace.append(f"DIMENSIONS  :  {ra}x{ca}")
    trace.append("-" * 54)
    for i in range(ra):
        for j in range(ca):
            a_v = fmt(A[i][j])
            b_v = fmt(B[i][j])
            c_v = fmt(A[i][j] + B[i][j])
            trace.append(f"  Result[{i+1},{j+1}]  =  {a_v}  +  {b_v}  =  {c_v}")
    return [[A[i][j] + B[i][j] for j in range(ca)] for i in range(ra)]


def op_subtraction(A, B, trace):
    ra, ca = len(A), len(A[0])
    rb, cb = len(B), len(B[0])
    if (ra, ca) != (rb, cb):
        raise MatrixError(f"Subtraction requires equal dimensions (Matrix A is {ra}x{ca}, Matrix B is {rb}x{cb}).")
    trace.append("OPERATION   :  Subtraction (Matrix A - Matrix B)")
    trace.append(f"DIMENSIONS  :  {ra}x{ca}")
    trace.append("-" * 54)
    for i in range(ra):
        for j in range(ca):
            a_v = fmt(A[i][j])
            b_v = fmt(B[i][j])
            c_v = fmt(A[i][j] - B[i][j])
            trace.append(f"  Result[{i+1},{j+1}]  =  {a_v}  -  {b_v}  =  {c_v}")
    return [[A[i][j] - B[i][j] for j in range(ca)] for i in range(ra)]


def op_multiplication(A, B, trace):
    ra, ca = len(A), len(A[0])
    rb, cb = len(B), len(B[0])
    if ca != rb:
        raise MatrixError(
            f"Multiplication requires columns of Matrix A ({ca}) == rows of Matrix B ({rb})."
        )
    res = [[0.0 for _ in range(cb)] for _ in range(ra)]
    trace.append("OPERATION   :  Multiplication (Matrix A × Matrix B)")
    trace.append(f"DIMENSIONS  :  ({ra}x{ca}) × ({rb}x{cb})  ->  ({ra}x{cb})")
    trace.append("-" * 54)
    for i in range(ra):
        for j in range(cb):
            parts = []
            for m in range(ca):
                res[i][j] += A[i][m] * B[m][j]
                parts.append(f"({fmt(A[i][m])} × {fmt(B[m][j])})")
            trace.append(f"  Result[{i+1},{j+1}]  =  {' + '.join(parts)}  =  {fmt(res[i][j])}")
    return res


def op_transpose(A, _B, trace):
    ra, ca = len(A), len(A[0])
    trace.append("OPERATION   :  Transpose (Matrix A Transposed)")
    trace.append(f"DIMENSIONS  :  {ra}x{ca}  ->  {ca}x{ra}   |   Rule: Result[row,col] = A[col,row]")
    trace.append("-" * 54)
    for i in range(ca):
        for j in range(ra):
            trace.append(f"  Result[{i+1},{j+1}]  =  A[{j+1},{i+1}]  =  {fmt(A[j][i])}")
    return [[A[j][i] for j in range(ra)] for i in range(ca)]


def _require_square(A, name):
    r, c = len(A), len(A[0])
    if r != c:
        raise MatrixError(f"{name} requires a square matrix (current size is {r}x{c}).")
    return [[float(v) for v in row] for row in A]


def op_determinant(A, _B, trace):
    M = _require_square(A, "Determinant")
    n = len(M)
    det = 1.0
    sign = 1.0
    trace.append("OPERATION   :  Determinant of Matrix A")
    trace.append(f"METHOD      :  Gaussian elimination with partial pivoting ({n}x{n})")
    trace.append("-" * 54)
    step = 1
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(M[row][col]))
        if abs(M[pivot][col]) < EPSILON:
            trace.append(f"  Step {step}: Column {col+1} pivot is 0  ->  Determinant = 0")
            return 0.0
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            sign *= -1.0
            trace.append(f"  Step {step}: Swap Row {col+1} <-> Row {pivot+1} (sign = {fmt(sign)})")
            step += 1
        pv = M[col][col]
        det *= pv
        for row in range(col + 1, n):
            factor = M[row][col] / pv
            for j in range(col + 1, n):
                M[row][j] -= factor * M[col][j]
            M[row][col] = 0.0
        trace.append(f"  Step {step}: Pivot ({col+1},{col+1}) = {fmt(pv)}")
        trace.append(matrix_text(M))
        step += 1
    result = sign * det
    result = 0.0 if abs(result) < EPSILON else result
    trace.append("-" * 54)
    trace.append(f"  Determinant  =  {fmt(sign)} × {fmt(det)}  =  {fmt(result)}")
    return result


def op_inverse(A, _B, trace):
    M = _require_square(A, "Inverse")
    n = len(M)
    aug = [M[i] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    trace.append("OPERATION   :  Inverse of Matrix A")
    trace.append(f"METHOD      :  Gauss-Jordan elimination on {n}x{2*n} [A | Identity]")
    trace.append("-" * 54)
    trace.append("  Initial [A | Identity]:")
    trace.append(matrix_text(aug))
    step = 1
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < EPSILON:
            raise MatrixError("Matrix is singular (determinant is 0); inverse does not exist.")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
            trace.append(f"  Step {step}: Swap Row {col+1} <-> Row {pivot+1}")
            step += 1
        pv = aug[col][col]
        aug[col] = [v / pv for v in aug[col]]
        trace.append(f"  Step {step}: Scale Row {col+1} by 1/{fmt(pv)}")
        trace.append(matrix_text(aug))
        step += 1
        for row in range(n):
            if row != col:
                factor = aug[row][col]
                aug[row] = [aug[row][j] - factor * aug[col][j] for j in range(2 * n)]
                trace.append(f"  Step {step}: Eliminate Col {col+1} in Row {row+1} (factor = {fmt(factor)})")
                trace.append(matrix_text(aug))
                step += 1
    trace.append("-" * 54)
    trace.append("  Right half of final matrix is the Inverse.")
    return [row[n:] for row in aug]


# Strictly 6 operations with clear, readable names
# (clear_name, description_line, fn, needs_b)
OPERATIONS = [
    ("Addition", "Matrix A + Matrix B", op_addition, True),
    ("Subtraction", "Matrix A − Matrix B", op_subtraction, True),
    ("Multiplication", "Matrix A × Matrix B", op_multiplication, True),
    ("Transpose", "Transpose of Matrix A", op_transpose, False),
    ("Determinant", "Determinant of Matrix A", op_determinant, False),
    ("Inverse", "Inverse of Matrix A", op_inverse, False),
]


class SlimScrollbar(tk.Canvas):
    """Sleek modern scrollbar."""

    def __init__(self, parent, orient="vertical", command=None, thickness=8, **kwargs):
        self.orient = orient
        self.command = command
        self.thickness = thickness
        self._start = 0.0
        self._end = 1.0
        self._drag_pos = None
        self._thumb_color = SCROLL_THUMB

        w = thickness if orient == "vertical" else 1
        h = 1 if orient == "vertical" else thickness
        super().__init__(
            parent,
            width=w,
            height=h,
            bg=SCROLL_TRACK,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )

        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", lambda _e: self._set_thumb_color(SCROLL_THUMB_HOVER))
        self.bind("<Leave>", lambda _e: self._set_thumb_color(SCROLL_THUMB))

    def _set_thumb_color(self, color):
        self._thumb_color = color
        self._redraw()

    def set(self, first, last):
        self._start = float(first)
        self._end = float(last)
        self._redraw()

    def _redraw(self, _event=None):
        self.delete("all")
        w = max(self.winfo_width(), 1)
        h = max(self.winfo_height(), 1)
        self.create_rectangle(0, 0, w, h, fill=SCROLL_TRACK, outline="")

        span = max(self._end - self._start, 0.08)
        if span >= 0.999:
            return

        if self.orient == "vertical":
            y0 = int(self._start * h)
            y1 = max(int(self._end * h), y0 + 24)
            y1 = min(y1, h)
            self.create_rectangle(1, y0, w - 1, y1, fill=self._thumb_color, outline="")
        else:
            x0 = int(self._start * w)
            x1 = max(int(self._end * w), x0 + 24)
            x1 = min(x1, w)
            self.create_rectangle(x0, 1, x1, h - 1, fill=self._thumb_color, outline="")

    def _on_click(self, event):
        if not self.command:
            return
        frac = (event.y / max(self.winfo_height(), 1)) if self.orient == "vertical" else (event.x / max(self.winfo_width(), 1))
        self.command("moveto", max(0.0, min(1.0, frac - (self._end - self._start) / 2)))
        self._drag_pos = event.y if self.orient == "vertical" else event.x

    def _on_drag(self, event):
        if not self.command or self._drag_pos is None:
            return
        pos = event.y if self.orient == "vertical" else event.x
        size = max(self.winfo_height() if self.orient == "vertical" else self.winfo_width(), 1)
        delta_frac = (pos - self._drag_pos) / size
        self._drag_pos = pos
        self.command("moveto", max(0.0, min(1.0, self._start + delta_frac)))

    def _on_release(self, _event):
        self._drag_pos = None


class SectionCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_CARD,
            highlightthickness=1,
            **kwargs,
        )


class MatrixCardBox:
    """
    Matrix input card supporting up to 10x10 rows & columns with smooth scrolling,
    auto-expanding cells when typing longer numbers, and mouse cell selection.
    """

    def __init__(self, parent, title, init_rows, init_cols, on_change, on_select, on_dim_change=None):
        self.on_change = on_change
        self.on_select = on_select
        self.on_dim_change = on_dim_change
        self.rows = init_rows
        self.cols = init_cols
        self.base_title = title

        self.vars = [[tk.StringVar() for _ in range(MAX_DIM)] for _ in range(MAX_DIM)]
        self.entries = [[None for _ in range(MAX_DIM)] for _ in range(MAX_DIM)]
        self.cell_frames = [[None for _ in range(MAX_DIM)] for _ in range(MAX_DIM)]

        self.card = SectionCard(parent, padx=16, pady=14)

        top = tk.Frame(self.card, bg=BG_CARD)
        top.pack(fill="x", pady=(0, 10))

        self.title_lbl = tk.Label(
            top,
            text=f"{title}  ({self.rows}×{self.cols})",
            font=("Segoe UI", 12, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
        )
        self.title_lbl.pack(side="left")

        dims = tk.Frame(top, bg=BG_CARD)
        dims.pack(side="right")

        self._make_dim_group(dims, "Rows", is_row=True)
        tk.Label(dims, text="   ", bg=BG_CARD).pack(side="left")
        self._make_dim_group(dims, "Cols", is_row=False)

        grid_holder = tk.Frame(self.card, bg=BG_CARD, height=280)
        grid_holder.pack(fill="x", expand=False)
        grid_holder.pack_propagate(False)

        self.canvas = tk.Canvas(grid_holder, bg=BG_CARD, highlightthickness=0, bd=0)
        self.vsb = SlimScrollbar(grid_holder, orient="vertical", command=self.canvas.yview, thickness=7)
        self.hsb = SlimScrollbar(grid_holder, orient="horizontal", command=self.canvas.xview, thickness=7)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_wrap = tk.Frame(self.canvas, bg=BG_CARD)
        self.win_id = self.canvas.create_window((0, 0), window=self.grid_wrap, anchor="nw")

        self.grid_wrap.bind("<Configure>", self._sync_scroll)
        self.canvas.bind("<Configure>", self._sync_scroll)

        for r in range(MAX_DIM):
            for c in range(MAX_DIM):
                cf = tk.Frame(
                    self.grid_wrap,
                    bg=BG_CARD,
                    highlightbackground=BORDER_CELL,
                    highlightthickness=1,
                )
                ent = tk.Entry(
                    cf,
                    textvariable=self.vars[r][c],
                    font=("Consolas", 11, "bold"),
                    justify="center",
                    width=MIN_CELL_W,
                    bg=BG_CARD,
                    fg=TEXT_PRIMARY,
                    insertbackground=BORDER_ACTIVE,
                    selectbackground="#DBEAFE",
                    selectforeground=TEXT_PRIMARY,
                    relief="flat",
                )
                ent.pack(padx=5, pady=4)
                ent.bind("<Button-1>", lambda _e, i=r, j=c: self.on_select(self, i, j))
                cf.bind("<Button-1>", lambda _e, i=r, j=c: self.on_select(self, i, j))
                ent.bind("<KeyRelease>", lambda _e, i=r, j=c: self._on_edit(i, j))

                self.cell_frames[r][c] = cf
                self.entries[r][c] = ent

        self._refresh_grid()

    def _make_dim_group(self, parent, label, is_row):
        tk.Label(
            parent,
            text=f"{label} (max {MAX_DIM}):",
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
        ).pack(side="left", padx=(0, 4))

        tk.Button(
            parent,
            text="−",
            font=("Segoe UI", 10, "bold"),
            width=2,
            bg=BG_SUBTLE,
            fg=TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            command=lambda: self.change_dim(-1 if is_row else 0, -1 if not is_row else 0),
        ).pack(side="left", padx=1)

        tk.Button(
            parent,
            text="+",
            font=("Segoe UI", 10, "bold"),
            width=2,
            bg=BG_SUBTLE,
            fg=TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            command=lambda: self.change_dim(1 if is_row else 0, 1 if not is_row else 0),
        ).pack(side="left", padx=(1, 0))

    def _sync_scroll(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        gw = self.grid_wrap.winfo_reqwidth()
        gh = self.grid_wrap.winfo_reqheight()
        x = max((cw - gw) // 2, 0)
        y = max((ch - gh) // 2, 0)
        self.canvas.coords(self.win_id, x, y)

    def _fit_cell(self, r, c):
        txt_len = len(self.vars[r][c].get().strip())
        w = max(MIN_CELL_W, min(MAX_CELL_W, txt_len + 2))
        self.entries[r][c].configure(width=w)

    def _on_edit(self, r, c):
        self._fit_cell(r, c)
        self.grid_wrap.update_idletasks()
        self._sync_scroll()
        self.on_change()

    def change_dim(self, dr=0, dc=0):
        self.set_size(self.rows + dr, self.cols + dc)

    def set_size(self, rows, cols):
        self.rows = max(1, min(MAX_DIM, rows))
        self.cols = max(1, min(MAX_DIM, cols))
        self._refresh_grid()
        if self.on_dim_change:
            self.on_dim_change()
        self.on_change()

    def _refresh_grid(self):
        self.title_lbl.configure(text=f"{self.base_title}  ({self.rows}×{self.cols})")
        for r in range(MAX_DIM):
            for c in range(MAX_DIM):
                cf = self.cell_frames[r][c]
                if r < self.rows and c < self.cols:
                    self._fit_cell(r, c)
                    cf.grid(row=r, column=c, padx=4, pady=4)
                else:
                    cf.grid_remove()
        self.grid_wrap.update_idletasks()
        self._sync_scroll()

    def get_matrix(self):
        mat = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                raw = self.vars[r][c].get().strip()
                if not raw:
                    row.append(0.0)
                else:
                    try:
                        val = float(raw)
                    except ValueError:
                        raise MatrixError(f"{self.base_title} ({r+1},{c+1}): '{raw}' is not a valid number.")
                    if not math.isfinite(val):
                        raise MatrixError(f"{self.base_title} ({r+1},{c+1}): value must be finite.")
                    row.append(val)
            mat.append(row)
        return mat

    def set_values(self, data):
        for r in range(MAX_DIM):
            for c in range(MAX_DIM):
                if r < len(data) and c < len(data[r]):
                    self.vars[r][c].set(str(data[r][c]))
                else:
                    self.vars[r][c].set("")
                self._fit_cell(r, c)
        self.grid_wrap.update_idletasks()
        self._sync_scroll()

    def clear_values(self):
        for r in range(MAX_DIM):
            for c in range(MAX_DIM):
                self.vars[r][c].set("")
                self._fit_cell(r, c)
        self.grid_wrap.update_idletasks()
        self._sync_scroll()


class MatrixOpsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MatrixOps — Matrix Calculator")
        self.root.geometry("1160x880")
        self.root.minsize(820, 620)
        self.root.configure(bg=BG_PAGE)

        self.op_map = {item[0]: item for item in OPERATIONS}
        self.active_op = tk.StringVar(value="Multiplication")
        self.active_cell = None
        self._last_copy_text = ""

        self._build_scrollable_page()
        self._build_sections()
        self.load_example()
        self._select_cell(self.matrix_a, 0, 0)

    def _build_scrollable_page(self):
        self.page_canvas = tk.Canvas(self.root, bg=BG_PAGE, highlightthickness=0, bd=0)
        self.page_vsb = SlimScrollbar(self.root, orient="vertical", command=self.page_canvas.yview, thickness=8)
        self.page_canvas.configure(yscrollcommand=self.page_vsb.set)

        self.page_vsb.pack(side="right", fill="y")
        self.page_canvas.pack(side="left", fill="both", expand=True)

        self.page_body = tk.Frame(self.page_canvas, bg=BG_PAGE, padx=28, pady=22)
        self.page_win = self.page_canvas.create_window((0, 0), window=self.page_body, anchor="n")

        self.page_body.bind("<Configure>", self._on_page_configure)
        self.page_canvas.bind("<Configure>", self._on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_page_configure(self, _event=None):
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        cw = event.width
        content_w = min(cw, 1140)
        x_left = max((cw - content_w) // 2, 0)
        self.page_canvas.itemconfigure(self.page_win, width=content_w)
        self.page_canvas.coords(self.page_win, x_left, 0)

    def _on_mousewheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is self.steps_text:
            self.steps_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        self.page_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _layout_matrices(self):
        wide_cols = max(self.matrix_a.cols, self.matrix_b.cols) >= 5
        narrow_win = self.root.winfo_width() < 1040

        for child in self.matrices_row.winfo_children():
            child.grid_forget()
            child.pack_forget()

        b_visible = bool(self.matrix_b_visible)
        if wide_cols or narrow_win or not b_visible:
            self.matrix_a.card.pack(fill="x", pady=(0, 14 if b_visible else 0))
            if b_visible:
                self.matrix_b.card.pack(fill="x")
        else:
            self.matrices_row.columnconfigure(0, weight=1, uniform="mat")
            self.matrices_row.columnconfigure(1, weight=1, uniform="mat")
            self.matrix_a.card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            self.matrix_b.card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def _build_sections(self):
        top_bar = tk.Frame(self.page_body, bg=BG_PAGE)
        top_bar.pack(fill="x", pady=(0, 18))

        left_hdr = tk.Frame(top_bar, bg=BG_PAGE)
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="Matrix Calculator",
            font=("Segoe UI", 26, "bold"),
            bg=BG_PAGE,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w")

        ops_list = " • ".join(op_name for op_name, *_rest in OPERATIONS) + f"  (up to {MAX_DIM}×{MAX_DIM})"
        tk.Label(
            left_hdr,
            text=ops_list,
            font=("Segoe UI", 11),
            bg=BG_PAGE,
            fg=TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        right_hdr = tk.Frame(top_bar, bg=BG_PAGE)
        right_hdr.pack(side="right", anchor="center")

        tk.Button(
            right_hdr,
            text="Load Example",
            command=self.load_example,
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            activebackground=BG_SUBTLE,
            relief="solid",
            bd=1,
            padx=14,
            pady=6,
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            right_hdr,
            text="Reset All",
            command=self.clear_all,
            font=("Segoe UI", 9, "bold"),
            bg=BG_SUBTLE,
            fg=TEXT_PRIMARY,
            activebackground="#E2E8F0",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        ).pack(side="left")

        self.matrices_row = tk.Frame(self.page_body, bg=BG_PAGE)
        self.matrices_row.pack(fill="x", pady=(0, 20))
        self.matrix_b_visible = True

        self.matrix_a = MatrixCardBox(
            self.matrices_row, "Matrix A", 3, 3, self.calculate, self._select_cell, self._layout_matrices
        )
        self.matrix_b = MatrixCardBox(
            self.matrices_row, "Matrix B", 3, 3, self.calculate, self._select_cell, self._layout_matrices
        )
        self.root.bind("<Configure>", lambda _e: self._layout_matrices())

        self._build_operation_section()
        self._build_result_section()
        self._build_steps_section()

    def _build_operation_section(self):
        tk.Label(
            self.page_body,
            text="1. Choose Operation",
            font=("Segoe UI", 13, "bold"),
            bg=BG_PAGE,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        card = SectionCard(self.page_body, padx=18, pady=16)
        card.pack(fill="x", pady=(0, 20))

        btn_grid = tk.Frame(card, bg=BG_CARD)
        btn_grid.pack(fill="x")

        self.op_buttons = {}
        for idx, (op_name, *_rest) in enumerate(OPERATIONS):
            r, c = divmod(idx, 3)
            btn_grid.columnconfigure(c, weight=1, uniform="ops")
            btn = tk.Button(
                btn_grid,
                text=op_name,
                font=("Segoe UI", 10, "bold"),
                pady=9,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda name=op_name: self._select_operation(name),
            )
            btn.grid(row=r, column=c, sticky="ew", padx=5, pady=5)
            self.op_buttons[op_name] = btn

        self.desc_lbl = tk.Label(
            card,
            text="Selected: Multiplication — Matrix A × Matrix B",
            font=("Segoe UI", 10, "bold"),
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
        )
        self.desc_lbl.pack(anchor="w", padx=5, pady=(10, 0))

    def _build_result_section(self):
        hdr = tk.Frame(self.page_body, bg=BG_PAGE)
        hdr.pack(fill="x", pady=(0, 8))

        self.result_sec_lbl = tk.Label(
            hdr,
            text="2. Result",
            font=("Segoe UI", 13, "bold"),
            bg=BG_PAGE,
            fg=TEXT_PRIMARY,
        )
        self.result_sec_lbl.pack(side="left")

        tk.Button(
            hdr,
            text="Copy Result",
            command=self.copy_result,
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            relief="solid",
            bd=1,
            padx=12,
            pady=4,
            cursor="hand2",
        ).pack(side="right")

        card = SectionCard(self.page_body, padx=18, pady=18)
        card.pack(fill="x", pady=(0, 20))

        res_holder = tk.Frame(card, bg=BG_CARD, height=280)
        res_holder.pack(fill="x", expand=False)
        res_holder.pack_propagate(False)

        self.res_canvas = tk.Canvas(res_holder, bg=BG_CARD, highlightthickness=0, bd=0)
        self.res_vsb = SlimScrollbar(res_holder, orient="vertical", command=self.res_canvas.yview, thickness=7)
        self.res_hsb = SlimScrollbar(res_holder, orient="horizontal", command=self.res_canvas.xview, thickness=7)
        self.res_canvas.configure(yscrollcommand=self.res_vsb.set, xscrollcommand=self.res_hsb.set)

        self.res_vsb.pack(side="right", fill="y")
        self.res_hsb.pack(side="bottom", fill="x")
        self.res_canvas.pack(side="left", fill="both", expand=True)

        self.result_grid_frame = tk.Frame(self.res_canvas, bg=BG_CARD)
        self.res_win_id = self.res_canvas.create_window((0, 0), window=self.result_grid_frame, anchor="nw")
        self.result_grid_frame.bind("<Configure>", self._sync_res_scroll)
        self.res_canvas.bind("<Configure>", self._sync_res_scroll)

        self.result_scalar_lbl = tk.Label(
            self.res_canvas,
            text="",
            font=("Consolas", 22, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
        )

        self.result_cells = []
        for r in range(MAX_DIM):
            row_items = []
            for c in range(MAX_DIM):
                sv = tk.StringVar()
                cf = tk.Frame(
                    self.result_grid_frame,
                    bg=BG_SUBTLE,
                    highlightbackground=BORDER_CELL,
                    highlightthickness=1,
                )
                lbl = tk.Label(
                    cf,
                    textvariable=sv,
                    font=("Consolas", 11, "bold"),
                    width=7,
                    height=2,
                    bg=BG_SUBTLE,
                    fg=TEXT_PRIMARY,
                )
                lbl.pack(padx=5, pady=4)
                row_items.append((cf, sv, lbl))
            self.result_cells.append(row_items)

    def _sync_res_scroll(self, _event=None):
        self.res_canvas.configure(scrollregion=self.res_canvas.bbox("all"))
        cw = self.res_canvas.winfo_width()
        ch = self.res_canvas.winfo_height()
        gw = self.result_grid_frame.winfo_reqwidth()
        gh = self.result_grid_frame.winfo_reqheight()
        self.res_canvas.coords(self.res_win_id, max((cw - gw) // 2, 0), max((ch - gh) // 2, 0))

    def _build_steps_section(self):
        tk.Label(
            self.page_body,
            text="3. Calculation Steps",
            font=("Segoe UI", 13, "bold"),
            bg=BG_PAGE,
            fg=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        card = SectionCard(self.page_body, padx=14, pady=14)
        card.pack(fill="x", pady=(0, 12))

        inner = tk.Frame(card, bg=BG_SUBTLE)
        inner.pack(fill="both", expand=True)

        self.steps_text = tk.Text(
            inner,
            font=("Consolas", 10),
            bg=BG_SUBTLE,
            fg=TEXT_PRIMARY,
            relief="flat",
            wrap="none",
            height=13,
            padx=12,
            pady=10,
            state="disabled",
        )
        steps_vsb = SlimScrollbar(inner, orient="vertical", command=self.steps_text.yview, thickness=7)
        steps_hsb = SlimScrollbar(inner, orient="horizontal", command=self.steps_text.xview, thickness=7)
        self.steps_text.configure(yscrollcommand=steps_vsb.set, xscrollcommand=steps_hsb.set)

        steps_vsb.pack(side="right", fill="y")
        steps_hsb.pack(side="bottom", fill="x")
        self.steps_text.pack(side="left", fill="both", expand=True)

    def _select_cell(self, grid_box, r, c):
        if self.active_cell:
            prev_box, pr, pc = self.active_cell
            prev_box.cell_frames[pr][pc].configure(highlightbackground=BORDER_CELL, highlightthickness=1)
            prev_box.entries[pr][pc].configure(bg=BG_CARD)

        self.active_cell = (grid_box, r, c)
        cf = grid_box.cell_frames[r][c]
        ent = grid_box.entries[r][c]
        cf.configure(highlightbackground=BORDER_ACTIVE, highlightthickness=2)
        ent.configure(bg=BG_CELL_ACTIVE)

        def _focus():
            ent.focus_set()
            ent.select_range(0, "end")
            ent.icursor("end")

        self.root.after_idle(_focus)

    def _select_operation(self, op_name):
        if op_name not in self.op_map:
            return
        self.active_op.set(op_name)
        _, desc, _fn, needs_b = self.op_map[op_name]
        self.desc_lbl.configure(text=f"Selected: {op_name} — {desc}")

        for name, btn in self.op_buttons.items():
            if name == op_name:
                btn.configure(bg=ACCENT_PRIMARY, fg=ACCENT_TEXT)
            else:
                btn.configure(bg=BG_SUBTLE, fg=TEXT_PRIMARY)

        self.matrix_b_visible = needs_b
        self._layout_matrices()
        self.calculate()

    def _set_steps(self, content):
        self.steps_text.configure(state="normal")
        self.steps_text.delete("1.0", "end")
        self.steps_text.insert("1.0", content)
        self.steps_text.configure(state="disabled")

    def _show_matrix_result(self, mat):
        self.result_scalar_lbl.place_forget()
        self.res_canvas.itemconfigure(self.res_win_id, state="normal")
        rows, cols = len(mat), len(mat[0])
        self.result_sec_lbl.configure(text=f"2. Result ({rows}×{cols})")

        for r in range(MAX_DIM):
            for c in range(MAX_DIM):
                cf, sv, lbl = self.result_cells[r][c]
                if r < rows and c < cols:
                    text_val = fmt(mat[r][c])
                    sv.set(text_val)
                    lbl.configure(width=max(7, len(text_val) + 2))
                    cf.grid(row=r, column=c, padx=4, pady=4)
                else:
                    sv.set("")
                    cf.grid_remove()

        self.result_grid_frame.update_idletasks()
        self._sync_res_scroll()

    def _show_scalar_result(self, val, op_name):
        self.res_canvas.itemconfigure(self.res_win_id, state="hidden")
        self.result_sec_lbl.configure(text=f"2. Result ({op_name})")
        self.result_scalar_lbl.configure(text=f"{op_name}  =  {fmt(val)}")
        self.result_scalar_lbl.place(relx=0.5, rely=0.5, anchor="center")

    def _clear_result(self):
        self.result_scalar_lbl.place_forget()
        self.res_canvas.itemconfigure(self.res_win_id, state="normal")
        self.result_sec_lbl.configure(text="2. Result")
        for r in range(MAX_DIM):
            for c in range(MAX_DIM):
                cf, sv, _lbl = self.result_cells[r][c]
                sv.set("")
                cf.grid_remove()

    def calculate(self):
        op_name = self.active_op.get()
        _, _desc, fn, needs_b = self.op_map[op_name]
        trace = []
        try:
            A = self.matrix_a.get_matrix()
            B = self.matrix_b.get_matrix() if needs_b else None

            out = fn(A, B, trace)
            self._set_steps("\n".join(trace))

            if isinstance(out, list):
                self._show_matrix_result(out)
                self._last_copy_text = matrix_text(out)
            else:
                self._show_scalar_result(float(out), op_name)
                self._last_copy_text = f"{op_name} = {fmt(float(out))}"
        except MatrixError as exc:
            self._clear_result()
            self._set_steps("Calculation paused:\n  " + str(exc))
            self._last_copy_text = ""

    def copy_result(self):
        if not self._last_copy_text:
            messagebox.showinfo("Copy Result", "No valid result to copy yet.", parent=self.root)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self._last_copy_text)

    def load_example(self):
        self.matrix_a.set_size(3, 3)
        self.matrix_b.set_size(3, 3)
        self.matrix_a.set_values([[2, -1, 3], [4, 0, 5], [1, 2, -2]])
        self.matrix_b.set_values([[1, 3, 0], [2, -1, 4], [5, 2, 1]])
        self.calculate()

    def clear_all(self):
        self.matrix_a.clear_values()
        self.matrix_b.clear_values()
        self._clear_result()
        self._set_steps("Cleared.")
        self._last_copy_text = ""


def main():
    root = tk.Tk()
    MatrixOpsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
