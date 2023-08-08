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
