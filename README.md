# ByteTrack for Caltech-UCSD Birds

## Tracking performance
### Results 
*Not yet reported.*

## Installation
### 1. Install the main dependencies.
```shell
git clone https://github.com/ifzhang/ByteTrack.git
cd ByteTrack
pip3 install -r requirements.txt
python3 setup.py develop
```

### 2. Install [pycocotools](https://github.com/cocodataset/cocoapi).

```shell
pip3 install cython; pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
```

### 3. Others
```shell
pip3 install cython_bbox
```

## Data preparation

Download [**Caltech-UCSD Birds**](https://www.vision.caltech.edu/datasets/cub_200_2011/) and save it in the `datasets` 
directory. The structure of the folder must look like this:

```
datasets
   |——————CaltechBirds
   |        └——————bounding_boxes.txt
   |        └——————classes.txt
   |        └——————image_class_labels.txt
   |        └——————images.txt
   |        └——————train_test_split.txt
   |        └——————images/
```

Then, you need to turn the dataset to COCO format:

```shell
cd <ByteTrack_HOME>
python tools/convert_birds_to_coco.py
```