import argparse
import json
import os
import pathlib

from PIL import Image


def get_image_info(filepath):
    image = Image.open(filepath)
    width, height = image.size
    data_dir, dataset, *path = filepath.parts
    return {'file_name': os.path.join(*path), 'width': width, 'height': height, 'frame_id': 1}, width, height


def create_annotation(filepath, image_size, starting_id):
    if not os.path.exists(filepath):
        return []
    im_width, im_height = image_size
    with open(filepath, 'r') as stream:
        lines = stream.readlines()
    lines = [line.strip() for line in lines]
    boxes = [line.split() for line in lines]
    im_annotations = []
    for index, *box in boxes:
        a, b, c, d, *x = (float(el) for el in box)
        left, width = int(im_width * a), int(im_width * c)
        top, height = int(im_height * b), int(im_height * d)
        im_annotations.append((left, top, width, height))
    return [{
        'id': starting_id + index,
        'track_id': -1,
        'bbox_vis': (left, top, width, height),
        'bbox': (left, top, width, height),
        'area': width * height,
        'iscrowd': 0  # Have no clue what this is!
    } for index, (left, top, width, height) in enumerate(im_annotations)]


if __name__ == '__main__':
    # Command Line Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='MixedPatches')
    parser.add_argument('--subsets', nargs='+', default=('train', 'val'))
    # Directories Setup
    args = parser.parse_args()
    data_dir = pathlib.Path('datasets') / args.dataset
    save_to = data_dir / 'annotations'
    if not save_to.exists():
        os.mkdir(save_to)
    # Classes for Export
    categories = [{'id': 1, 'name': 'Bird'}]
    # Images and Annotations
    images = [[] for subset in args.subsets]
    annotations = [[] for subset in args.subsets]
    # Processing
    for split, name in enumerate(args.subsets):
        split_dir = data_dir / name
        filenames = os.listdir(split_dir / 'images')
        for filename in filenames:
            image_id = len(images[split]) + 1
            sample, extension = os.path.splitext(filename)
            image_info, *image_size = get_image_info(split_dir / 'images' / filename)
            images[split].append({'id': image_id, 'video_id': image_id, **image_info})
            annotations_starting_id = len(annotations[split]) + 1
            image_annotations = create_annotation(split_dir / 'labels' / f'{sample}.txt', image_size, annotations_starting_id)
            annotations[split].extend({'image_id': image_id, 'category_id': 1, **annotation} for annotation in image_annotations)
    for split, name in enumerate(args.subsets):
        output = {'categories': categories, 'images': images[split], 'annotations': annotations[split]}
        json.dump(output, open(save_to / f'{name}.json', 'w'))
