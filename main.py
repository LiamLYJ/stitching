import argparse
import os 
import sys
import glob
import cv2
import dataset
import utils
import geometry
import pano_pair

parser = argparse.ArgumentParser()
parser.add_argument("--results_dir", type=str, default="results", help="where to put results")
parser.add_argument("--workspace_dir", type=str, default='stitching_tmp', help="where to put tmp data")
parser.add_argument("--image_dir", type=str, default="./datasets/images", help="src image dir")
parser.add_argument("--image_data_fn", type=str, default='./datasets/image_data.txt', help="size of each image batch")
parser.add_argument("--resize_scale", type=float, default=0.5, help="downsampling scale")
parser.add_argument("--valid_ratio", type=float, default=0.2, help="valid ratio for valid matching top 2")



def main(opt):
    print ('prepareing dataset...')
    all_images, data_matrix = dataset.prepare(opt.image_data_fn, opt.image_dir, opt.workspace_dir)

    print ('use IMU to de-transform images...')
    geometry.changePerspective(all_images, data_matrix, opt.workspace_dir, opt.resize_scale)

    print ('stitching image')
    image_list = sorted(glob.glob(os.path.join(opt.workspace_dir, "*.png")))
    detector = cv2.xfeatures2d.SURF_create(300)
    result = cv2.imread(image_list[0])
    for i in range(1, len(image_list)):
        image = cv2.imread(image_list[i])

        try:
            result = pano_pair.combine(result, image, detector)
            cv2.imwrite(os.path.join(opt.results_dir, "int_res_%d.png"%(i)), result)
            print ("Stitched " + str(i + 1) + " Images")

        except:
            print ("Fail " + str(i))
            #cv2.imwrite("results/int_res" + str(i) + ".JPG", result)

        h, w = result.shape[:2]

        if h > 4000 and w > 4000:

            if h > 4000:
                hx = 4000/h

                h = h*hx
                w = w*hx

            elif w > 4000:
                wx = 4000/w

                w = w*wx
                h = h*wx

            result = cv2.resize(result, (int(w), int(h)))

    cv2.imwrite(os.path.join(opt.results_dir, "final_result.png"), result)

if __name__ == '__main__':
    opt = parser.parse_args()
    print (opt)

    os.makedirs(opt.results_dir, exist_ok= True)
    os.makedirs(opt.workspace_dir, exist_ok= True)

    main(opt)