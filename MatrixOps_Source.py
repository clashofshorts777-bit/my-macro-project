"""
MatrixOps - Final Project Version
Tkinter GUI integrated with a pure-Python matrix computation backend.
Run: python matrixops_alpha.py
No third-party packages required (Tkinter is included with most Python installations).
"""
import math
import tkinter as tk
from tkinter import ttk, messagebox

EPSILON = 1e-12

class MatrixError(ValueError):
    """Raised for invalid matrix data or mathematically invalid operations."""

def validate_matrix(matrix):
    if not matrix or not matrix[0]:
        raise MatrixError("Matrix must have at least one row and one column.")
    cols = len(matrix[0])
    for row in matrix:
        if len(row) != cols:
            raise MatrixError("All rows must have the same number of values.")
        for value in row:
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise MatrixError("Matrix values must be finite numbers.")
    return len(matrix), cols

def parse_matrix(text, name="Matrix"):
    rows = []
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        try:
            row = [float(token) for token in line.replace(",", " ").split()]
        except ValueError:
            raise MatrixError(f"{name}: enter only numeric values, separated by spaces or commas.")
        rows.append(row)
    if not rows:
        raise MatrixError(f"{name}: enter at least one row of values.")
    validate_matrix(rows)
    return rows

def fmt(x):
    if abs(x - round(x)) < 1e-10:
        return str(int(round(x)))
    return f"{x:.6g}"

def matrix_text(M):
    return "\n".join("[ " + "   ".join(fmt(float(x)) for x in row) + " ]" for row in M)

def add(A, B):
    ra, ca = validate_matrix(A); rb, cb = validate_matrix(B)
    if (ra, ca) != (rb, cb):
        raise MatrixError("Addition requires A and B to have equal dimensions.")
    return [[A[i][j] + B[i][j] for j in range(ca)] for i in range(ra)]

def subtract(A, B):
    ra, ca = validate_matrix(A); rb, cb = validate_matrix(B)
    if (ra, ca) != (rb, cb):
        raise MatrixError("Subtraction requires A and B to have equal dimensions.")
    return [[A[i][j] - B[i][j] for j in range(ca)] for i in range(ra)]

def multiply(A, B, trace=None):
    ra, ca = validate_matrix(A); rb, cb = validate_matrix(B)
    if ca != rb:
        raise MatrixError("Multiplication requires columns of A to equal rows of B.")
    result = [[0.0 for _ in range(cb)] for _ in range(ra)]
    for i in range(ra):
        for j in range(cb):
            terms = []
            for k in range(ca):
                result[i][j] += A[i][k] * B[k][j]
                terms.append(f"{fmt(A[i][k])}×{fmt(B[k][j])}")
            if trace is not None:
                trace.append(f"C[{i+1},{j+1}] = " + " + ".join(terms) + f" = {fmt(result[i][j])}")
    return result

def transpose(A, trace=None):
    r, c = validate_matrix(A)
    result = [[A[i][j] for i in range(r)] for j in range(c)]
    if trace is not None:
        trace.append(f"Transpose: rows and columns are exchanged ({r}×{c} becomes {c}×{r}).")
        for i in range(r):
            for j in range(c):
                trace.append(f"Aᵀ[{j+1},{i+1}] = A[{i+1},{j+1}] = {fmt(A[i][j])}")
    return result

def _square(A):
    r, c = validate_matrix(A)
    if r != c:
        raise MatrixError("Determinant and inverse require a square matrix.")
    return [[float(x) for x in row] for row in A]

def determinant(A, trace=None):
    M = _square(A); n = len(M); det = 1.0; sign = 1.0
    if trace is not None:
        trace.append("Method: Gaussian elimination with partial pivoting.")
        trace.append("The determinant is the product of diagonal pivots, adjusted for row-swap sign.")
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < EPSILON:
            if trace is not None: trace.append(f"Column {col+1}: pivot is approximately zero; determinant = 0.")
            return 0.0
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]; sign *= -1
            if trace is not None: trace.append(f"Swap rows {col+1} and {pivot+1}; sign becomes {int(sign)}.")
        pv = M[col][col]; det *= pv
        if trace is not None: trace.append(f"Pivot at row {col+1}, column {col+1}: {fmt(pv)}.")
        for row in range(col+1, n):
            factor = M[row][col] / pv
            for j in range(col+1, n): M[row][j] -= factor * M[col][j]
            M[row][col] = 0.0
            if trace is not None:
                trace.append(f"Eliminate row {row+1} using factor {fmt(factor)}.")
                trace.append("    " + matrix_text(M).replace("\n", "\n    "))
    result = sign * det
    if trace is not None: trace.append(f"det(A) = row-swap sign × pivot product = {fmt(sign)} × {fmt(det)} = {fmt(result)}.")
    return 0.0 if abs(result) < EPSILON else result

def inverse(A, trace=None):
    M = _square(A); n = len(M)
    aug = [M[i] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    if trace is not None:
        trace.append("Method: Gauss–Jordan elimination with partial pivoting.")
        trace.append("Augment A with the identity matrix; reduce the left side to identity.")
        trace.append(matrix_text(aug))
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < EPSILON:
            raise MatrixError("Matrix is singular (or numerically singular); inverse does not exist.")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
            if trace is not None: trace.append(f"Swap rows {col+1} and {pivot+1}.")
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        if trace is not None:
            trace.append(f"Normalize pivot row {col+1} by dividing by {fmt(pv)}.")
            trace.append(matrix_text(aug))
        for row in range(n):
            if row != col:
                factor = aug[row][col]
                aug[row] = [aug[row][j] - factor * aug[col][j] for j in range(2*n)]
                if trace is not None:
                    trace.append(f"Eliminate column {col+1} from row {row+1} (factor {fmt(factor)}).")
                    trace.append(matrix_text(aug))
    if trace is not None: trace.append("The right half of the final augmented matrix is A⁻¹.")
    return [row[n:] for row in aug]

OPERATIONS = {
    "Addition": (add, 2),
    "Subtraction": (subtract, 2),
    "Multiplication": (multiply, 2),
    "Transpose": (transpose, 1),
    "Determinant": (determinant, 1),
    "Inverse": (inverse, 1),
}

class MatrixOpsApp:
    def __init__(self, root):
        self.root = root
        root.title("MatrixOps | Final Project Version")
        root.geometry("1050x760")
        root.minsize(850, 600)
        self.operation = tk.StringVar(value="Addition")
        self._build()

    def _build(self):
        outer = ttk.Frame(self.root, padding=12); outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="MatrixOps", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Matrix calculator • Final project version • Step-by-step algorithm trace").pack(anchor="w", pady=(0, 10))
        controls = ttk.Frame(outer); controls.pack(fill="x", pady=(0, 8))
        ttk.Label(controls, text="Operation:").pack(side="left")
        combo = ttk.Combobox(controls, textvariable=self.operation, values=list(OPERATIONS), state="readonly", width=18)
        combo.pack(side="left", padx=8); combo.bind("<<ComboboxSelected>>", self._operation_changed)
        ttk.Label(controls, text="Enter each row on a new line; separate values with spaces or commas.").pack(side="left", padx=12)
        matrices = ttk.Frame(outer); matrices.pack(fill="x", expand=False)
        self.box_a = self._matrix_panel(matrices, "Matrix A", "1 2\n3 4")
        self.box_b = self._matrix_panel(matrices, "Matrix B", "5 6\n7 8")
        self.box_b.master.pack_configure(side="left", fill="both", expand=True, padx=(8,0))
        actions = ttk.Frame(outer); actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Calculate", command=self.calculate).pack(side="left")
        ttk.Button(actions, text="Load Example", command=self.load_example).pack(side="left", padx=8)
        ttk.Button(actions, text="Clear", command=self.clear).pack(side="left")
        self.status = tk.StringVar(value="Ready. Enter matrix values and select Calculate.")
        ttk.Label(outer, textvariable=self.status, foreground="#245a35").pack(anchor="w", pady=(0, 6))
        split = ttk.Panedwindow(outer, orient="horizontal"); split.pack(fill="both", expand=True)
        result_frame = ttk.LabelFrame(split, text="Result", padding=8)
        trace_frame = ttk.LabelFrame(split, text="Algorithm trace", padding=8)
        split.add(result_frame, weight=1); split.add(trace_frame, weight=2)
        self.result = tk.Text(result_frame, wrap="none", height=14, width=28, font=("Consolas", 11), state="disabled")
        self.result.pack(fill="both", expand=True)
        self.trace = tk.Text(trace_frame, wrap="word", height=14, font=("Consolas", 10), state="disabled")
        sy = ttk.Scrollbar(trace_frame, orient="vertical", command=self.trace.yview); self.trace.configure(yscrollcommand=sy.set)
        self.trace.pack(side="left", fill="both", expand=True); sy.pack(side="right", fill="y")
        self._operation_changed()

    def _matrix_panel(self, parent, title, initial):
        panel = ttk.LabelFrame(parent, text=title, padding=8); panel.pack(side="left", fill="both", expand=True)
        txt = tk.Text(panel, height=6, width=30, font=("Consolas", 11), undo=True)
        txt.pack(fill="both", expand=True); txt.insert("1.0", initial)
        return txt

    def _operation_changed(self, event=None):
        op = self.operation.get()
        self.box_b.master.pack_forget()
        if OPERATIONS[op][1] == 2:
            self.box_b.master.pack(side="left", fill="both", expand=True, padx=(8,0))
        self.status.set(f"Selected operation: {op}.")

    def _set_text(self, widget, content):
        widget.configure(state="normal"); widget.delete("1.0", "end"); widget.insert("1.0", content); widget.configure(state="disabled")

    def calculate(self):
        op = self.operation.get(); fn, count = OPERATIONS[op]; trace = []
        try:
            A = parse_matrix(self.box_a.get("1.0", "end"), "Matrix A")
            if count == 2:
                B = parse_matrix(self.box_b.get("1.0", "end"), "Matrix B")
                result = fn(A, B, trace) if op in ("Multiplication",) else fn(A, B)
            else:
                result = fn(A, trace) if op in ("Transpose", "Determinant", "Inverse") else fn(A)
            if isinstance(result, list):
                result_text = matrix_text(result)
            else:
                result_text = fmt(float(result))
            self._set_text(self.result, result_text)
            if not trace:
                if op == "Addition": trace = ["Element-wise addition: C[i,j] = A[i,j] + B[i,j].", "Each pair of corresponding entries is added."]
                elif op == "Subtraction": trace = ["Element-wise subtraction: C[i,j] = A[i,j] − B[i,j].", "Each entry of B is subtracted from the corresponding entry of A."]
            self._set_text(self.trace, "\n".join(trace) if trace else "No trace available.")
            self.status.set(f"{op} completed successfully.")
        except (MatrixError, ValueError, OverflowError) as exc:
            self._set_text(self.result, "No result")
            self._set_text(self.trace, "Calculation stopped because the input or operation was invalid.\n\n" + str(exc))
            self.status.set("Please correct the input and calculate again.")
            messagebox.showerror("MatrixOps - Input or calculation error", str(exc), parent=self.root)

    def load_example(self):
        self.box_a.delete("1.0", "end"); self.box_a.insert("1.0", "4 7\n2 6")
        self.box_b.delete("1.0", "end"); self.box_b.insert("1.0", "1 2\n3 4")
        self.status.set("Example matrices loaded. Select an operation and calculate.")

    def clear(self):
        self.box_a.delete("1.0", "end"); self.box_b.delete("1.0", "end")
        self._set_text(self.result, ""); self._set_text(self.trace, "")
        self.status.set("Inputs and outputs cleared.")

def main():
    root = tk.Tk()
    MatrixOpsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
