import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSlider, QFileDialog,
    QMessageBox, QStatusBar,
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from main import read_file, compute_density

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiDAR Density Map")
        self.resize(900, 700)

        self._density = None
        self._x_bins = None
        self._y_bins = None
        self._input_stem = None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # File picker
        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Input file:"))
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Select a .las, .laz or .csv file…")
        self.file_edit.setReadOnly(True)
        file_row.addWidget(self.file_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        # Settings
        settings_row = QHBoxLayout()
        settings_row.addWidget(QLabel("Cell size (m):"))
        self.cell_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.cell_size_slider.setRange(1, 100)
        self.cell_size_slider.setValue(10)
        self.cell_size_slider.setFixedWidth(160)
        self.cell_size_label = QLabel("10 m")
        self.cell_size_slider.valueChanged.connect(lambda v: self.cell_size_label.setText(f"{v} m"))
        self.cell_size_slider.sliderReleased.connect(self._try_run)
        settings_row.addWidget(self.cell_size_slider)
        settings_row.addWidget(self.cell_size_label)
        settings_row.addSpacing(20)
        settings_row.addWidget(QLabel("Classes:"))
        self.classes_edit = QLineEdit("5")
        self.classes_edit.setFixedWidth(100)
        self.classes_edit.setToolTip("Comma-separated class numbers, e.g. 3,4,5")
        self.classes_edit.textChanged.connect(self._try_run)
        settings_row.addWidget(self.classes_edit)
        settings_row.addStretch()
        layout.addLayout(settings_row)

        # Matplotlib canvas
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self._show_placeholder()

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _try_run(self):
        if not self.file_edit.text():
            return
        try:
            self._parse_classes()
        except ValueError:
            return
        self._run()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select LiDAR file", "",
            "LiDAR files (*.las *.laz *.csv);;All files (*)",
        )
        if path:
            self.file_edit.setText(path)
            self._run()

    def _parse_classes(self):
        text = self.classes_edit.text().strip()
        try:
            return {int(c.strip()) for c in text.split(",")}
        except ValueError:
            raise ValueError(f"Invalid classes: '{text}'. Use comma-separated integers, e.g. 3,4,5")

    def _run(self):
        path = self.file_edit.text()
        if not path:
            QMessageBox.warning(self, "No file selected", "Please select an input file first.")
            return

        try:
            classes = self._parse_classes()

            self.status.showMessage("Reading file…")
            QApplication.processEvents()
            df = read_file(path)

            available = sorted(int(c) for c in df["classification"].unique())

            self.status.showMessage("Computing density…")
            QApplication.processEvents()
            self._density, self._x_bins, self._y_bins = compute_density(
                df, classes, cell_size=self.cell_size_slider.value()
            )
            self._input_stem = Path(path).stem

            matched = df["classification"].isin(classes).sum()
            if matched == 0:
                self.status.showMessage(
                    f"No points found for classes {sorted(classes)}. "
                    f"Available classes: {available}"
                )
                return

            self._plot()
            self.status.showMessage(
                f"{len(df):,} points — available classes: {available}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status.showMessage("Error")

    def _show_placeholder(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, "Upload a file to begin", ha="center", va="center",
                fontsize=14, color="grey", transform=ax.transAxes)
        ax.axis("off")
        self.canvas.draw()

    def _plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        im = ax.imshow(
            self._density.T,
            origin="lower",
            extent=[self._x_bins[0], self._x_bins[-1], self._y_bins[0], self._y_bins[-1]],
            cmap="YlGn",
            vmin=0, vmax=1,
        )
        self.figure.colorbar(im, ax=ax, label="Relative density (0–1)")
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_title("LiDAR Density Map")
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
