import argparse
import json
import os
import pathlib

import scipy.io as io
from PIL import Image


def get_image_info(filepath):
    image = Image.open(data_dir / 'images' / filepath)
    width, height = image.size
    return {'file_name': os.path.join('images', filepath), 'width': width, 'height': height, 'frame_id': 1}


def get_image_annotation(filepath, image_id, individual):
    if individual:
        category_id, *rest = filepath.split('.')
    else:
        category_id = 1
    filepath = data_dir / 'annotations-mat' / filepath
    filepath, extension = os.path.splitext(filepath)
    annotation = io.loadmat(f'{filepath}.mat')
    box = annotation['bbox']  # Left, Top, Right, Bottom
    left, top, right, bottom = [box[0, 0][i].item() for i in range(4)]
    box = [left, top, right - left, bottom - top]
    return {
        'category_id': int(category_id),
        'image_id': image_id,
        'track_id': -1,
        'bbox_vis': box,
        'bbox': box,
        'area': (right - left) * (bottom - top),
        'iscrowd': 0  # Have no clue what this is!
    }


if __name__ == '__main__':
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='datasets/CaltechBirds')
    parser.add_argument('--individual', action='store_true')
    parser.add_argument('--merged', action='store_true')
    parser.add_argument('--skip-annotations', action='store_true')
    # Directories Setup
    args = parser.parse_args()
    data_dir = pathlib.Path(args.dir)
    save_to = data_dir / 'annotations'
    if not save_to.exists():
        os.mkdir(save_to)
    # Initializations
    classes = data_dir / 'lists' / 'classes.txt'
    with open(classes) as stream:
        classes = [line.rstrip().split() for line in stream.readlines()]
    if args.individual:
        categories = [{'id': index, 'name': name} for index, name in classes]
    else:
        categories = [{'id': 1, 'name': 'Any_Bird'}]
    # Exporting
    subsets = ['files'] if args.merged else ['train', 'test']
    for subset in subsets:
        output = {'images': None, 'annotations': None, 'categories': categories}
        print(f'Processing {subset}.txt ...')
        # Image Files
        with open(data_dir / 'lists' / f'{subset}.txt') as stream:
            filepaths = [line.rstrip() for line in stream.readlines()]
        images = map(get_image_info, filepaths)
        output['images'] = [{'id': index, 'video_id': index, **di} for index, di in enumerate(images)]
        # Annotations
        annotations = []
        if not args.skip_annotations:
            for index, filepath in enumerate(filepaths):
                annotation = get_image_annotation(filepath, index, args.individual)
                annotations.append({'id': len(annotations), **annotation})
        output['annotations'] = annotations
        # Saving
        json.dump(output, open(save_to / f'{subset if not args.merged else "train"}.json', 'w'))
