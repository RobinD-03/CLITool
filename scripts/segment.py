import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

def segment(pcd,distance):
    plane_model, inliers = pcd.segment_plane(distance_threshold=distance,
                                            ransac_n=3,
                                            num_iterations=1000)
    [a, b, c, d] = plane_model
    print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")

    inlier_cloud = pcd.select_by_index(inliers)
    inlier_cloud.paint_uniform_color([1.0, 0, 0])
    outlier_cloud = pcd.select_by_index(inliers, invert=True)

    return inlier_cloud, outlier_cloud

def cluster(outlier_cloud,epsilon,minimum):
    with o3d.utility.VerbosityContextManager(
            o3d.utility.VerbosityLevel.Debug) as cm:
        labels = np.array(
            outlier_cloud.cluster_dbscan(eps=epsilon, min_points=minimum, print_progress=True))

    max_label = labels.max()
    print(f"point cloud has {max_label + 1} clusters")
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0
    outlier_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])

    return outlier_cloud

def main():
    pcd = o3d.io.read_point_cloud("/home/robin/Desktop/open3d/filtered_house.ply")

    inlier_cloud, outlier_cloud = segment(pcd,0.25)

    outlier_cloud = cluster(outlier_cloud,1,25)

    o3d.visualization.draw_geometries([inlier_cloud,outlier_cloud],
                                    zoom=0.8,
                                    front=[-0.4999, -0.1659, -0.8499],
                                    lookat=[2.1813, 2.0619, 2.0999],
                                    up=[0.1204, -0.9852, 0.1215])
    
if __name__ == '__main__':
    main()