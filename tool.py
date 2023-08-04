import argparse
import os
import sys
import open3d as o3d
from scripts import visualize
from scripts import filter
from scripts import segment


def save_point_cloud(new_cloud, name): 
    o3d.io.write_point_cloud(name, new_cloud)

path = None

def main():
    parser = argparse.ArgumentParser(description="PointCloud Tool")
    
    # Subparsers for downsample and visualize
    subparsers = parser.add_subparsers(dest="command")
    
    # Subparser for 'downsample' command
    parser_downsample = subparsers.add_parser("d", help="Downsample Point cloud")
    parser_downsample.add_argument("input_file", help="Path to the input file")
    parser_downsample.add_argument("output_file", help="Path to the output file")
    parser_downsample.add_argument("voxel_size", type=float, default=0.05, help="Voxel size")
    parser_downsample.set_defaults(func=downsample)
    
    parser_visualize = subparsers.add_parser("v", help="Visualize Point cloud")
    parser_visualize.add_argument("path", nargs="?", default=None, help="Paths to visualize")
    parser_visualize.set_defaults(func=visualize_point_cloud)
    
    args = parser.parse_args()
    args.func(args)

def downsample(args):
    new_cloud = filter.downsampling(args.input_file, args.voxel_size)
    save_point_cloud(new_cloud, args.output_file)
    global path
    path = args.output_file

def visualize_point_cloud(args):
    global path
    if not args.paths and path:
        visualize.visualize(path)
    elif args.paths:
        for path in args.paths:
            visualize.visualize(path)
    else:
        sys.exit("No path specified for visualization.")

if __name__ == "__main__":
    main()