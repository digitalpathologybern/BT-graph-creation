import glob
import os
import numpy as np
from lxml import etree as ET
import argparse
import re
import shutil
import pandas as pd

from coord_to_xml import create_asap_xml
from xml_to_txt_file import process_xml_files


def setup_output_folders(output_path):
    # set / create the output
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    # make the output folders
    xml_output = os.path.join(output_path, 'asap_xml')
    if not os.path.isdir(xml_output):
        os.mkdir(xml_output)
    txt_output = os.path.join(output_path, 'coordinates_txt')
    if not os.path.isdir(txt_output):
        os.mkdir(txt_output)

    return xml_output, txt_output


def in_circle(center_x, center_y, radius, x, y):
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


def parse_tma_coord_csv(coord_csvs):
    all_core_coord = []
    for file_path in coord_csvs:
        if os.path.isfile(file_path):
            df = pd.read_csv(file_path, sep=";")
            df.dropna(subset=['Core Unique ID'], inplace=True)
            df.insert(0, 'TMA_filename', re.search(r'Coordinates_(.*).csv', file_path).group(1))
            df['Core Unique ID'] = df['Core Unique ID'].astype(int)
            all_core_coord.append(df)
        else:
            print(f'File {file_path} does not exist.')
    all_core_coord = pd.concat(all_core_coord, ignore_index=True, sort=False)
    all_core_coord = all_core_coord[all_core_coord.columns.drop(list(all_core_coord.filter(regex='microns')))]
    return all_core_coord


def create_hotspot_only_txt_files(txt_files_to_process, xml_output, txt_output, all_cores, overwrite=False):
    output_text_files = []
    error_files = []
    for file in txt_files_to_process:
        print('Processing file {}'.format(os.path.basename(file)))
        if os.path.isfile(file):
            # load the file
            coords = np.loadtxt(file)
            #
            output_txt_file = ""
            # if not os.path.isfile(output_txt_file) or overwrite:
            #     np.savetxt(output_txt_file, to_save, fmt='%.4f')
            else:
                print('The coordinates file {} already exists'.format(output_txt_file))
        else:
            print('File {} does not exist. Continuing...'.format(file_path))
            error_files.append(file_path)

    create_asap_xml(txt_output, xml_output)


if __name__ == '__main__':
    # Expects the hotspot files to have the same name as the matching coordinate files
    parser = argparse.ArgumentParser()
    parser.add_argument("--tma-coord-folder", type=str, required=True)
    parser.add_argument("--output-folder", type=str, required=True)
    parser.add_argument("--coordinate-txt-files", type=str, required=True)
    parser.add_argument("--overwrite", type=bool, required=False, default=False)
    args = parser.parse_args()

    tma_coord_folder = args.tma_coord_folder

    output_path = args.output_folder

    core_output, txt_output = setup_output_folders(output_path)

    coor_txt_files_path = os.path.join(args.coordinate_txt_files, r'*_coordinates_*.txt')
    all_txt_files = glob.glob(coor_txt_files_path)
    txt_files_to_process = {os.path.basename(file): file for file in list(set([re.search(r'(.*)_coordinates', f).group(1) for f in all_txt_files]))}

    # get the TMA core coordinates
    file_ids = set([os.path.basename(f) for f in txt_files_to_process])
    tma_coord_csv_files = glob.glob(os.path.join(tma_coord_folder, '*.csv'))
    tma_coord = parse_tma_coord_csv(tma_coord_csv_files)

    # create the hotspot asap and txt files
    create_hotspot_only_txt_files(txt_files_to_process, core_output, txt_output, tma_coord, args.overwrite)