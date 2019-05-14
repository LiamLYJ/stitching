# stitching

Drone image stitching 

make sure the images using are from DJI shot (need IMU data from drone image)

checkout flags in main.py

"--results_dir", type=str, default="results", help="where to put results")
"--workspace_dir", type=str, default='stitching_tmp', help="where to put tmp data")
"--image_dir", type=str, default="./datasets/images", help="src image dir")
"--image_data_fn", type=str, default='./datasets/image_data.txt', help="size of each image batch")
"--resize_scale", type=float, default=0.5, help="downsampling scale")
"--valid_ratio", type=float, default=0.2, help="valid ratio for valid matching top 2")


dependency:
requirements.txt

