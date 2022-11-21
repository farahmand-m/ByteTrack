import argparse
import json
import os
import pathlib

import scipy.io as io
from PIL import Image


def get_image_info(filepath):
    image = Image.open(filepath)
    width, height = image.size
    data_dir, dataset, *path = filepath.parts
    return {'file_name': os.path.join(*path), 'width': width, 'height': height, 'frame_id': 1}


def create_annotation(filepath, starting_id):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as stream:
        info = json.load(stream)
    shapes, boxes = info.get('shapes') or [], []
    for shape in shapes:
        (left, top), (right, bottom) = shape['points']
        # Some points don't seem to be in the right order.
        left, right = min(left, right), max(left, right)
        top, bottom = min(top, bottom), max(top, bottom)
        boxes.append((left, top, right - left, bottom - top))
    return [{
        'id': starting_id + index,
        'track_id': -1,
        'bbox_vis': (left, top, width, height),
        'bbox': (left, top, width, height),
        'area': width * height,
        'iscrowd': 0  # Have no clue what this is!
    } for index, (left, top, width, height) in enumerate(boxes)]


if __name__ == '__main__':
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='datasets/BirdsLab')
    # Directories Setup
    args = parser.parse_args()
    data_dir = pathlib.Path(args.dir)
    save_to = data_dir / 'annotations'
    if not save_to.exists():
        os.mkdir(save_to)
    # Classes for Export
    categories = [{'id': 1, 'name': 'Bird'}]
    # Images and Annotations
    subsets = ('train', 'test')
    images = [[] for subset in subsets]
    annotations = [[] for subset in subsets]
    # Processing
    for split, name in enumerate(subsets):
        split_dir = data_dir / name / 'images_and_jsons'
        filenames = os.listdir(split_dir)
        filenames = [os.path.splitext(filename) for filename in filenames]
        samples = set(name for name, extension in filenames)
        for sample in samples:
            image_id = len(images[split]) + 1
            image_info = get_image_info(split_dir / f'{sample}.jpg')
            images[split].append({'id': image_id, 'video_id': image_id, **image_info})
            annotations_starting_id = len(annotations[split]) + 1
            image_annotations = create_annotation(split_dir / f'{sample}.json', annotations_starting_id)
            annotations[split].extend({'image_id': image_id, 'category_id': 1, **annotation} for annotation in image_annotations)
    for split, name in enumerate(subsets):
        output = {'images': images[split], 'annotations': annotations[split], 'categories': categories}
        json.dump(output, open(save_to / f'{name}.json', 'w'))
