#!/usr/bin/env python

import rasterio
import os
import argparse
import csv
import numpy
from tqdm import tqdm

#Argument parsing
parser = argparse.ArgumentParser("Tool for pulling out CHELSA data for specific coordinate. Outputs to stdout (recommend redirect)")
parser.add_argument("-d", "--directory", dest="chel_d", type=str, help="Directory of CHELSA tif files", required=True)
parser.add_argument("-t", "--latitude", dest="lat", type=float, help="Latitude of coordiante of interest", required=True)
parser.add_argument("-g", "--longitude", dest="long", type=float, help="Longitude of coordiante of interest", required=True)
parser.add_argument("-i", "--inputages", dest="in_ages", type=str, help="Files contains ages to interpolate values", required=True)
parser.add_argument("-a", "--alldates", dest="alldates", action="store_true", help="Outputs separate file with all data from CHELSA images")
args = parser.parse_args()

# List of chelsa data [[age, value], ...]
chelsa_data = []

# Loops through tif images
for filename in tqdm(os.listdir(args.chel_d)):
    if not filename.endswith(".tif"):
        continue
    f = os.path.join(args.chel_d, filename)

    # Pulls out age from file name and converts it to years BP
    kabp = round((2 - (float(f.split("_")[-2]) * 0.1)) * 1000, 1)

    with rasterio.open(f) as img:
        # Gets row and column index from coordinates
        rowind, colind = img.index(args.long, args.lat)
        band1 = img.read(1)
        chelsa_data.append([kabp, band1[rowind, colind]])

# Outputs chelsa data if requested
if args.alldates:
    with open("chelsa_output.csv", "w") as outf:
        outputwriter = csv.writer(outf, delimiter="\t")
        outputwriter.writerows(chelsa_data)

# Ages to interpolate
ages_interp = []

# Populates ages to interpolate list
with open(args.in_ages) as inf:
    for line in inf:
        ages_interp.append(float(line.rstrip()))

# Interpolate values
interp_values = numpy.interp(ages_interp, [item[0] for item in chelsa_data], [item[1] for item in chelsa_data])

# Outputs interpolated values
for i in range(len(ages_interp)):
    print(f"{ages_interp[i]}\t{interp_values[i]}")
