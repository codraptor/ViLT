from .utils import (
    # inception_normalize,
    MinMaxResize,
)
from torchvision import transforms
import torch
from .randaug import RandAugment


def pixelbert_transform(size=800):
    longer = int((1333 / 800) * size)
    # return transforms.Compose(
    return torch.nn.Sequential(
            MinMaxResize(shorter=size, longer=longer),
            # transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    )


def pixelbert_transform_randaug(size=800):
    longer = int((1333 / 800) * size)
    trs = transforms.Compose(
        [
            MinMaxResize(shorter=size, longer=longer),
            transforms.ToTensor(),
            inception_normalize,
        ]
    )
    trs.transforms.insert(0, RandAugment(2, 9))
    return trs
