import argparse
import json
import os
import pathlib

import scipy.io as io
from PIL import Image


def read_list(filepath, flatten, type=None):
    with open(data_dir / filepath) as stream:
        items = [line.rstrip().split() for line in stream.readlines()]
    li = [rest for index, *rest in items]
    if type is not None:
        li = [[type(el) for el in item] for item in li]
    if flatten:
        li = [el for item in li for el in item]
    return li


def get_image_info(filepath):
    image = Image.open(data_dir / 'images' / filepath)
    width, height = image.size
    return {'file_name': os.path.join('images', filepath), 'width': width, 'height': height, 'frame_id': 1}


def create_annotation(box):
    left, top, width, height = box
    return {
        'track_id': -1,
        'bbox_vis': box, 'bbox': box,
        'area': width * height,
        'iscrowd': 0  # Have no clue what this is!
    }


if __name__ == '__main__':
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='datasets/CaltechBirds')
    parser.add_argument('--separate', action='store_true')
    # Directories Setup
    args = parser.parse_args()
    data_dir = pathlib.Path(args.dir)
    save_to = data_dir / 'annotations'
    if not save_to.exists():
        os.mkdir(save_to)
    # Lists and Labels
    classes = read_list('classes.txt', flatten=True)
    filepaths = read_list('images.txt', flatten=True)
    boxes = read_list('bounding_boxes.txt', flatten=False, type=float)
    splits = read_list('train_test_split.txt', flatten=True, type=int)
    labels = read_list('image_class_labels.txt', flatten=True, type=int)
    assert len(filepaths) == len(boxes) == len(splits) == len(labels)
    # Classes for Export
    if not args.separate:
        categories = [{'id': index + 1, 'name': name} for index, name in enumerate(classes)]
    else:
        categories = [{'id': 1, 'name': 'Any_Bird'}]
    # Images and Annotations
    subsets = ('train', 'test')
    images = [[] for subset in subsets]
    annotations = [[] for subset in subsets]
    for filepath, box, split, label in zip(filepaths, boxes, splits, labels):
        index = len(images[split]) + 1
        category_id = label if args.separate else 1
        images[split].append({'id': index, 'video_id': index, **get_image_info(filepath)})
        annotations[split].append({'id': index, 'image_id': index, 'category_id': category_id, **create_annotation(box)})
    for split, name in enumerate(subsets):
        output = {'images': images[split], 'annotations': annotations[split], 'categories': categories}
        json.dump(output, open(save_to / f'{name}.json', 'w'))
