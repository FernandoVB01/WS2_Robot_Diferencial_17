"""Render the original CAD mesh coordinates (millimetres) with project colours.

Optional documentation tool; requires numpy and matplotlib, not ROS.
"""
from pathlib import Path
import struct

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
MESHES = ROOT / 'src/Samuel_WS2_description/meshes'
OUTPUT = ROOT / 'imagenes'
COLOURS = {
    'base_link': '#1464d9',
    'lidar_1': '#ff791f',
    'camera_1': '#303644',
    'castor_1': '#929eae',
    'left_wheel_1': '#202632',
    'right_wheel_1': '#202632',
}


def triangles(name):
    data = (MESHES / f'{name}.stl').read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attr', '<u2')])
    mesh = np.frombuffer(data, dtype=dtype, count=count, offset=84)['vertices'].copy()
    # Subdivide long triangles for reliable depth ordering in Matplotlib's renderer.
    for _ in range(6):
        lengths = np.linalg.norm(mesh - np.roll(mesh, 1, axis=1), axis=2)
        mask = lengths.max(axis=1) > 8
        if not mask.any():
            break
        a, b, c = mesh[mask].transpose(1, 0, 2)
        ab, bc, ca = (a+b)/2, (b+c)/2, (c+a)/2
        mesh = np.concatenate([mesh[~mask], np.stack([a, ab, ca], axis=1),
                               np.stack([ab, b, bc], axis=1), np.stack([ca, bc, c], axis=1),
                               np.stack([ab, bc, ca], axis=1)])
    return mesh


def draw(ax, elev, azim, title):
    geometry = []
    colours = []
    for name, colour in COLOURS.items():
        mesh = triangles(name)
        geometry.append(mesh)
        colours.extend([colour] * len(mesh))
    ax.add_collection3d(Poly3DCollection(np.concatenate(geometry), facecolors=colours,
                                       linewidths=0, shade=True, antialiased=False))
    ax.set(xlim=(-120, 120), ylim=(-100, 100), zlim=(-5, 100))
    ax.set_box_aspect((240, 200, 105))
    ax.set_proj_type('ortho')
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=16, color='#24334d', pad=2)


def main():
    OUTPUT.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(10, 7), facecolor='white')
    draw(fig.add_subplot(111, projection='3d'), 26, 38, 'Robot diferencial · Grupo 17')
    fig.text(.5, .03, 'Geometría STL exportada de Fusion 360', ha='center', color='#526078')
    fig.savefig(OUTPUT / 'robot_cad_isometrica.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    fig = plt.figure(figsize=(13, 6), facecolor='white')
    draw(fig.add_subplot(121, projection='3d'), 90, -90, 'Vista superior')
    draw(fig.add_subplot(122, projection='3d'), 0, -90, 'Vista lateral')
    fig.text(.5, .04, 'Grupo 17 · Mallas originales con los colores del proyecto', ha='center', color='#526078')
    fig.savefig(OUTPUT / 'robot_cad_vistas.png', dpi=170, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    main()
