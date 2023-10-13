""" LAS file generator
    Run this file in a singularity container to avoid installing pdal
        singularity pull docker://qgis/qgis
        singularity shell qgis_latest.sif

Returns:
    A las file for each of the .PLY files
"""
import numpy as np
import open3d as o3d
import json
import os
import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="PLY to LAS converter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-pc",
        "--pointcloud",
        help="name of the .ply files",
        type=str,
        nargs="+",
        required=True,
    )
    return parser.parse_args()


def conversion_pipeline(input_file, output_file):
    pipeline_definition = {
        "pipeline": [
            {"type": "readers.ply", "filename": input_file},
            {
                "type": "writers.las",
                "format": 1.4,
                "scale_x": "0.000000001",
                "scale_y": "0.000000001",
                "scale_z": "0.000000001",
                "a_srs": "EPSG:32612",
                "filename": output_file,
            },
        ]
    }
    pipeline_json = json.dumps(pipeline_definition)
    with open("pipeline.json", "w") as f:
        f.write(pipeline_json)
    os.system("pdal pipeline pipeline.json")


def main():
    args = get_args()
    for pointcloud in args.pointcloud:
        pcd = o3d.io.read_point_cloud(pointcloud)
        points = np.asarray(pcd.points)
        centered = points - pcd.get_center()
        pcd.points = o3d.utility.Vector3dVector(centered)
        o3d.io.write_point_cloud(
            f"{pointcloud.split('/')[-1].split('.')[0]}_centered.ply", pcd
        )
        conversion_pipeline(
            f"{pointcloud.split('/')[-1].split('.')[0]}_centered.ply",
            f"{pointcloud.split('/')[-1].split('.')[0]}.las",
        )


# --------------------------------------------------
if __name__ == "__main__":
    main()
