import numpy as np
from PIL import Image

OLYMPIC_COLORS = {
    'Y': (255, 255, 0),  # yellow
    'B': (0, 0, 255),    # blue
    'K': (0, 0, 0),      # black
    'G': (0, 255, 0),    # green
    'R': (255, 0, 0)     # red
}


def count_pixels(image_path):
    with Image.open(image_path) as image:
        image_array = np.array(image)
        mask = np.isin(image_array, list(OLYMPIC_COLORS.values())).all(axis=-1)
        pixel_counts = {}
        for color, rgb in OLYMPIC_COLORS.items():
            count = np.sum(np.all(image_array[mask] == rgb, axis=-1))
            pixel_counts[color] = count
        return pixel_counts


def find_logo_centers(image_path):
    with Image.open(image_path) as image:
        image_array = np.array(image)
        centers = []
        for color1, color2 in [('blue', 'yellow'), ('black', 'yellow'), ('green', 'black'), ('green', 'red')]:
            mask1 = np.all(image_array == OLYMPIC_COLORS[color1], axis=-1)
            mask2 = np.all(image_array == OLYMPIC_COLORS[color2], axis=-1)
            combined_mask = np.logical_and(mask1, mask2)
            labeled, _ = ndimage.label(combined_mask)
            for i in range(1, labeled.max() + 1):
                blob_mask = labeled == i
                ys, xs = np.where(blob_mask)
                x_center = int(np.mean(xs))
                y_center = int(np.mean(ys))
                if validate_logo(image_array, x_center, y_center):
                    centers.append((color1, color2, x_center, y_center))
        return centers


if __name__ == '__main__':
    image_path = input().strip()
    color_counts = count_pixels(image_path)
    for color, count in color_counts.items():
        print(f'{color}: {count}')
