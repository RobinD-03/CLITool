import argparse
import os
import sys
import open3d as o3d
from scripts import visualize
from scripts import filter
from scripts import segment
import json


class PointCloudTool():
    def __init__(self):
        self.config_file = 'config.json'
        self.paths = self.load_paths()
        self.parser = self.create_parser()

    def load_paths(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return []

    def save_paths(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.paths, f)

    def clear_configuration(self):
        self.paths.clear()
        self.save_paths()

    def create_parser(self):
        parser = argparse.ArgumentParser(description='Point Cloud Tool')

        parser.add_argument('--clear-config', action='store_true', help='Clears config file that saves previous paths')

        subparsers = parser.add_subparsers(dest="command")
    
        # Subparser for downsample
        parser_downsample = subparsers.add_parser("d", help="Downsample Point cloud")
        parser_downsample.add_argument("input_file", help="Path to the input file")
        parser_downsample.add_argument("output_file", help="Path to the output file")
        parser_downsample.add_argument('-v',"--voxel_size", type=float, help="Voxel size, 0.05 if not specified")
        parser_downsample.set_defaults(func=self.downsample)
        
        # Subparser for visualize
        parser_visualize = subparsers.add_parser("v", help="Visualize Point cloud")
        parser_visualize.add_argument("path", nargs="?", default=None, help="Path to visualize, last path given will be visualized if none is specified")
        parser_visualize.set_defaults(func=self.visualize)

        # Subparser for filtering 
        parser_filter = subparsers.add_parser('f', help="Point Cloud Statistical outlier removal")
        parser_filter.add_argument('filter_input_file', help="Path to input file")
        parser_filter.add_argument('filter_output_file', help="Path to output file")
        parser_filter.add_argument('--neighbors', '-n', type=int, help="Number of neighbors, default value: 20")
        parser_filter.add_argument('--ratio', '-r', type=float, help="filtering ratio, default value: 2.0")
        parser_filter.set_defaults(func=self.filtering)
        
        # Subparser for segmentation
        parser_segment = subparsers.add_parser('s', help="Point Cloud Plane Segmentation")
        parser_segment.add_argument('segment_input_file', help="Path to input file")
        parser_segment.add_argument('segment_output_file', help="Path to output file")
        parser_segment.add_argument('--distance', '-dt', type=float, help="Distnace Threshold Between Points")
        parser_segment.set_defaults(func=self.segmenting)

        # Subparser for clustering
        parser_cluster = subparsers.add_parser('c', help="Point Cloud Clustering")
        parser_cluster.add_argument('cluster_input_file', help="Path to input file")
        parser_cluster.add_argument('cluster_output_file', help="Path to output file")
        parser_cluster.add_argument('--epsilon', '-e', type=float, help="Epsilon")
        parser_cluster.add_argument('--minimum', '-m', type=float, help="Minimum Points to create a Cluster")
        parser_cluster.set_defaults(func=self.clustering)

        return parser


    def save_point_cloud(self,new_cloud,name):
        o3d.io.write_point_cloud(name, new_cloud)


    def downsample(self, args):
        if args.voxel_size is None:
            vs=0.05
        else:
            vs=args.voxel_size
        new_cloud = filter.downsampling(args.input_file, vs)
        self.save_point_cloud(new_cloud, args.output_file)
        
        self.paths.append({
            'input': args.input_file,
            'output': args.output_file,
        })
        self.save_paths()

    def visualize(self, args):
        if not args.path and not self.paths:
            sys.exit("No path specified")
        else:
            if self.paths:
                latest_path = self.paths[-1]

        if args.path:
            if os.path.exists(args.path):
                self.paths.append({
                    'input': args.path,
                    'output': None,
                })
                self.save_paths()
                visualize.visualize(args.path)
            else:
                sys.exit("Specified path does not exist")
        elif latest_path:
            if latest_path.get('output') and os.path.exists(latest_path['output']):
                visualize.visualize(latest_path['output'])
            elif latest_path.get('input') and os.path.exists(latest_path['input']):
                visualize.visualize(latest_path['input'])

    def filtering(self, args):
        if args.neighbors is None:
            n=20
        else:
            n=args.neighbors
        
        if args.ratio is None:
            r=2.0
        else:
            r=args.ratio
        
        filtered = filter.filtering(args.filter_input_file, n, r)
        self.save_point_cloud(filtered, args.filter_output_file)

        self.paths.append({
            'input':args.filter_input_file,
            'output':args.filter_output_file,
        })

        self.save_paths()

    def segmenting(self, args):
        if args.distance is None:
            dt = 0.25
        else:
            dt = args.distance

        inlier, outlier = segment.segment(args.segment_input_file, dt)

        finalCloud = inlier + outlier

        self.save_point_cloud(finalCloud, args.segment_output_file)

        self.paths.append({
            'input':args.segment_input_file,
            'output':args.segment_output_file,
        })
        self.save_paths()

    def clustering(self,args):
        if args.epsilon is None:
            eps = 1
        else:
            eps=args.epsilon

        if args.minimum is None:
            minimum = 10
        else:
            minimum = args.minimum

        clustered = segment.cluster(args.cluster_input_file,eps,minimum)

        self.save_point_cloud(clustered, args.cluster_output_file)
        self.paths.append({
            'input':args.cluster_input_file,
            'output':args.cluster_output_file,
        })
        self.save_paths()


    def run(self):
        args = self.parser.parse_args()

        if args.clear_config:
            self.clear_configuration()
            print('Cleared Configuration')
        else:
            args.func(args)


if __name__ == '__main__':
    tool = PointCloudTool()
    tool.run()
