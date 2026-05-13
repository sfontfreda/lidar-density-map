# lidar-density-map

A desktop app for visualising LiDAR point cloud density by classification class. Load a `.las`, `.laz` or `.csv` file and get an interactive density map instantly.

## What it does

Given a LiDAR point cloud, the app divides the terrain into a grid of cells and computes — for each cell — what fraction of points belong to the selected class(es). The result is rendered as a colour heatmap (0 = no points of that class, 1 = all points belong to that class).

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
.venv\Scripts\python.exe src\app.py
```

- **Browse** — select a `.las`, `.laz` or `.csv` input file
- **Cell size** — grid resolution in metres (1–100 m)
- **Classes** — comma-separated class numbers to filter (e.g. `3,4,5`)

The map updates automatically when any parameter changes. The status bar shows the available classes in the loaded file.

## LiDAR standard classes

| Code | Meaning |
|------|---------|
| 0 | Unclassified |
| 1 | Unassigned |
| 2 | Ground |
| 3 | Low vegetation |
| 4 | Medium vegetation |
| 5 | High vegetation |
| 6 | Building |
| 9 | Water |
| 17 | Bridge deck |

## CSV format

If using a CSV file, it must have the following columns: `x`, `y`, `z`, `classification`.

## Dependencies

- [laspy](https://github.com/laspy/laspy) — LAS/LAZ file reading
- [numpy](https://numpy.org) — point binning and density computation
- [matplotlib](https://matplotlib.org) — density map rendering
- [pandas](https://pandas.pydata.org) — data handling
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — desktop GUI
