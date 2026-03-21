# 
#
#
# This script will convert a given measured hdf5 file into three different hdf5 file, ready for reconstruction.
# 

# Open the measured projections 


# create universial changing function to modify the projections . 


# create an identical hdf5 file with all attributes from t he original file 

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

import h5py
import numpy as np


class HDFFileEditor:
    """
    Lean HDF5 editor for copying a file and replacing selected datasets.

    Design:
    - original file stays untouched
    - changed datasets are stored in memory in `modified_datasets`
    - when saving, the original file structure is copied and modified datasets
      are written in place of the originals
    """

    def __init__(self, input_path: Union[str, Path]) -> None:
        self.input_path = Path(input_path)

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.modified_datasets: Dict[str, np.ndarray] = {}

    def read_dataset(self, dataset_path: str) -> np.ndarray:
        """
        Read a dataset from the original file as a NumPy array.

        If the dataset was already modified in memory, return the modified version.
        """
        if dataset_path in self.modified_datasets:
            return self.modified_datasets[dataset_path]

        with h5py.File(self.input_path, "r") as h5file:
            if dataset_path not in h5file:
                raise KeyError(f"Dataset path not found: {dataset_path}")

            obj = h5file[dataset_path]
            if not isinstance(obj, h5py.Dataset):
                raise TypeError(f"Path is not a dataset: {dataset_path}")

            return obj[()]

    def replace_dataset(self, dataset_path: str, new_data: np.ndarray) -> None:
        """
        Store a replacement dataset in memory.

        The change is not written to disk until save_as() is called.
        """
        if not isinstance(new_data, np.ndarray):
            raise TypeError("new_data must be a NumPy ndarray.")

        with h5py.File(self.input_path, "r") as h5file:
            if dataset_path not in h5file:
                raise KeyError(f"Dataset path not found: {dataset_path}")

            obj = h5file[dataset_path]
            if not isinstance(obj, h5py.Dataset):
                raise TypeError(f"Path is not a dataset: {dataset_path}")

        self.modified_datasets[dataset_path] = new_data

    def list_paths(self) -> list[str]:
        """
        List all group and dataset paths in the file.
        """
        paths: list[str] = []

        with h5py.File(self.input_path, "r") as h5file:
            def visitor(name: str, obj) -> None:
                paths.append("/" + name)

            h5file.visititems(visitor)

        return ["/"] + paths

    def save_as(self, output_path: Union[str, Path]) -> Path:
        """
        Create a new HDF5 file:
        - copy all groups, datasets, and attributes from the original file
        - replace datasets that were modified in memory
        """
        output_path = Path(output_path)

        with h5py.File(self.input_path, "r") as src, h5py.File(output_path, "w") as dst:
            self._copy_group(src, dst, current_path="/")

        return output_path

    def _copy_group(self, src_group, dst_group, current_path: str) -> None:
        """
        Recursively copy a group and all its contents.
        """
        # Copy attributes of current group
        for key, value in src_group.attrs.items():
            dst_group.attrs[key] = value

        for name, item in src_group.items():
            item_path = self._join_hdf_path(current_path, name)

            if isinstance(item, h5py.Group):
                new_group = dst_group.create_group(name)
                self._copy_group(item, new_group, item_path)

            elif isinstance(item, h5py.Dataset):
                data_to_write = self.modified_datasets.get(item_path, item[()])
                self._copy_dataset(item, dst_group, name, data_to_write)

            else:
                raise TypeError(f"Unsupported HDF5 object type at {item_path}: {type(item)}")

    def _copy_dataset(
        self,
        src_dataset: h5py.Dataset,
        dst_group: h5py.Group,
        name: str,
        data: np.ndarray,
    ) -> None:
        """
        Copy one dataset, preserving attributes and most storage settings.
        """
        create_kwargs = {}

        if src_dataset.chunks is not None:
            create_kwargs["chunks"] = src_dataset.chunks

        if src_dataset.compression is not None:
            create_kwargs["compression"] = src_dataset.compression

        if src_dataset.compression_opts is not None:
            create_kwargs["compression_opts"] = src_dataset.compression_opts

        if src_dataset.shuffle is not None:
            create_kwargs["shuffle"] = src_dataset.shuffle

        if src_dataset.fletcher32 is not None:
            create_kwargs["fletcher32"] = src_dataset.fletcher32

        if src_dataset.scaleoffset is not None:
            create_kwargs["scaleoffset"] = src_dataset.scaleoffset

        if src_dataset.maxshape is not None:
            create_kwargs["maxshape"] = src_dataset.maxshape

        new_dataset = dst_group.create_dataset(name, data=data, **create_kwargs)

        for key, value in src_dataset.attrs.items():
            new_dataset.attrs[key] = value

    @staticmethod
    def _join_hdf_path(parent: str, child: str) -> str:
        """
        Join HDF5 path parts safely.
        """
        if parent == "/":
            return f"/{child}"
        return f"{parent}/{child}"



def bin_2x2_stack(data: np.ndarray) -> np.ndarray:
    """
    Bin the last two dimensions of an image stack by 2x2 averaging.

    Example:
        (N, H, W) -> (N, H//2, W//2)

    If H or W is odd, the last row/column is discarded.
    """
    if data.ndim < 2:
        raise ValueError("Input array must have at least 2 dimensions.")

    h = data.shape[-2]
    w = data.shape[-1]

    h2 = h // 2
    w2 = w // 2

    trimmed = data[..., : h2 * 2, : w2 * 2]

    binned = (
        trimmed[..., 0::2, 0::2]
        + trimmed[..., 0::2, 1::2]
        + trimmed[..., 1::2, 0::2]
        + trimmed[..., 1::2, 1::2]
    ) / 4.0

    return binned

if __name__ == '__main__':
    import numpy as np
    from pathlib import Path
    import os

    from pathlib import Path

    SCRIPT_DIR = Path(__file__).resolve().parent

    input_file = SCRIPT_DIR / "measured.h5"
    

    
    output_file = SCRIPT_DIR / "modified.h5"
    projection_path = "/entry/data/data"  



    hdf = HDFFileEditor(input_file)

    # Read projections
    projections = hdf.read_dataset(projection_path)
    print("Original shape:", projections.shape)
    # Example temporary modification
    #modified = projections.astype(np.float32) * 2.0

    binned = bin_2x2_stack(projections)
    print("Binned shape:", binned.shape)

    # Replace dataset in memory
    hdf.replace_dataset(projection_path, binned)

    # Save full new file
    hdf.save_as(output_file)

    print(f"Saved modified file to: {output_file}")




