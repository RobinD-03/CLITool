import open3d as o3d
import sys
import os


def downsampling(ply,size):
    ply = o3d.io.read_point_cloud(ply)
    down = ply.voxel_down_sample(voxel_size=size)
    return down


def filtering(ply, neighbors, ratio):
    ply = o3d.io.read_point_cloud(ply)
    filter, indices = ply.remove_statistical_outlier(nb_neighbors=neighbors,
                                                 std_ratio=ratio)
    return filter


def main(ply):
    down = downsampling(ply,0.25)
    filtered = filtering(down,20, 2.0)
    o3d.visualization.draw_geometries([filtered])
    print('passed\n')
    head, tail = os.path.split(ply)
    print(tail)
    new_file_name = f"filtered_{tail}"
    o3d.io.write_point_cloud(new_file_name,filtered)

    

if __name__ == '__main__':
    main(sys.argv[1])