import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_sample_data(output_path, n_points=5000, seed=42):
    rng = np.random.default_rng(seed)

    x = rng.uniform(0, 100, n_points)
    y = rng.uniform(0, 100, n_points)
    z = rng.uniform(0, 30, n_points)
    classification = rng.integers(1, 7, n_points)

    df = pd.DataFrame({"x": x, "y": y, "z": z, "classification": classification})
    df.to_csv(output_path, index=False)
    print(f"Fitxer generat: {output_path} ({n_points} punts)")


def compute_density(df, target_classes, cell_size=10):
    x_bins = np.arange(df["x"].min(), df["x"].max() + cell_size, cell_size)
    y_bins = np.arange(df["y"].min(), df["y"].max() + cell_size, cell_size)

    total, _, _ = np.histogram2d(df["x"], df["y"], bins=[x_bins, y_bins])

    mask = df["classification"].isin(target_classes)
    target, _, _ = np.histogram2d(df[mask]["x"], df[mask]["y"], bins=[x_bins, y_bins])

    density = np.where(total > 0, target / total, 0)

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

    plt.colorbar(im, ax=ax, label="Densitat relativa (0–1)")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Mapa de densitat per classe")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Mapa guardat: {output_path}")

def export_csv(density, x_bins, y_bins, output_path):
    cell_size = x_bins[1] - x_bins[0]
    rows = []

    for i in range(density.shape[0]):
        for j in range(density.shape[1]):
            rows.append({
                "x_centre": round(x_bins[i] + cell_size / 2, 2),
                "y_centre": round(y_bins[j] + cell_size / 2, 2),
                "density": round(float(density[i, j]), 4),
            })

    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"CSV exportat: {output_path}")


if __name__ == "__main__":
    generate_sample_data("data/sample.csv")

    df = pd.read_csv("data/sample.csv")

    target_classes = {5}
    density, x_bins, y_bins = compute_density(df, target_classes, cell_size=10)

    plot_density(density, x_bins, y_bins, "output/density_map.png")
    export_csv(density, x_bins, y_bins, "output/density.csv")
