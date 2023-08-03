import open3d as o3d
import sys


def visualize(ply):
    ptcld = o3d.io.read_point_cloud(ply)
    o3d.visualization.draw_geometries([ptcld])


def main(ptcld):
    visualize(ptcld)


if __name__ == '__main__':
    main(sys.argv[1])