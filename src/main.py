from pathlib import Path

import laspy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_file(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
        for col in ("x", "y", "z", "classification"):
            if col not in df.columns:
                raise ValueError(f"CSV is missing required column: '{col}'")
    elif suffix in (".las", ".laz"):
        las = laspy.read(path)
        df = pd.DataFrame({
            "x": las.x.scaled_array(),
            "y": las.y.scaled_array(),
            "z": las.z.scaled_array(),
            "classification": np.array(las.classification),
        })
    else:
        raise ValueError(f"Unsupported format: '{suffix}'. Use .csv, .las or .laz")

    print(f"File read: {file_path} ({len(df):,} points)")
    return df


def generate_sample_data(output_path, n_points=5000, seed=42):
    rng = np.random.default_rng(seed)

    x = rng.uniform(0, 100, n_points)
    y = rng.uniform(0, 100, n_points)
    z = rng.uniform(0, 30, n_points)
    classification = rng.integers(1, 7, n_points)

    df = pd.DataFrame({"x": x, "y": y, "z": z, "classification": classification})
    df.to_csv(output_path, index=False)
    print(f"File generated: {output_path} ({n_points} points)")


def compute_density(df, target_classes, cell_size=10):
    x_bins = np.arange(df["x"].min(), df["x"].max() + cell_size, cell_size)
    y_bins = np.arange(df["y"].min(), df["y"].max() + cell_size, cell_size)

    total, _, _ = np.histogram2d(df["x"], df["y"], bins=[x_bins, y_bins])

    mask = df["classification"].isin(target_classes)
    target, _, _ = np.histogram2d(df[mask]["x"], df[mask]["y"], bins=[x_bins, y_bins])

    density = np.divide(target, total, out=np.zeros_like(target, dtype=float), where=total > 0)

    return density, x_bins, y_bins


def plot_density(density, x_bins, y_bins, output_path):
    fig, ax = plt.subplots(figsize=(8, 6))

    im = ax.imshow(
        density.T,
        origin="lower",
        extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]],
        cmap="YlGn",
        vmin=0, vmax=1,
    )

    plt.colorbar(im, ax=ax, label="Relative density (0–1)")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Density map by class")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Map saved: {output_path}")


if __name__ == "__main__":
    generate_sample_data("data/sample.csv")

    df = pd.read_csv("data/sample.csv")

    target_classes = {5}
    density, x_bins, y_bins = compute_density(df, target_classes, cell_size=10)

    plot_density(density, x_bins, y_bins, "output/density_map.png")
