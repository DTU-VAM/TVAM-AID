from dataclasses import dataclass
from cil.framework import ImageData, ImageGeometry
import numpy as np

@dataclass(frozen=True)
class VoxelRegions:
    """Voxel masks defining the in-part, out-of-part and external regions of the voxel array."""
    inPart: np.ndarray
    outPart: np.ndarray
    external: np.ndarray

@dataclass(frozen=True)
class Target:
    """Target geometry and its voxel-region masks."""
    image: ImageData
    regions: VoxelRegions

def loadTargetGeometry(path: str):
    """Load a binary target from a numpy file."""
    targetData = np.load(path).astype(float)
    
    _checkTargetIsBinary(targetData)
    _checkTargetDimensions(targetData)

    if targetData.ndim == 3:
        # for astra order
        targetData = np.transpose(targetData, (2,1,0))

    regions = _getRegionMasks(targetData)
    imageGeometry = _getImageGeometry(targetData)
    
    image = imageGeometry.allocate()
    image.fill(targetData)
    
    return Target(image=image, regions=regions)

def _checkTargetIsBinary(target: np.ndarray):
    """Checks if the target array is binary."""
    if not np.all((target==0) | (target==1)):
        raise ValueError('Target must contain only binary values 0 and 1')

def _checkTargetDimensions(target: np.ndarray):
    """Checks if the target is 2D or 3D, and has a square x-y cross section"""
    if target.ndim not in (2,3):
        raise ValueError('Target must be a 2D or 3D array')
        
    if target.shape[0] != target.shape[1]:
            raise ValueError('Target cross section must have equal x and y dimensions')

def _getRegionMasks(array: np.ndarray):
    """Get the masks for in-part, out-of-part, and external regions."""
    circleMask = getCircleMask(array)
    regions = VoxelRegions(
        inPart = np.logical_and(array>0, circleMask),
        outPart = np.logical_and(array<1, circleMask),
        external = np.logical_not(circleMask),
    )
    return regions

def _getImageGeometry(array: np.ndarray):
    """Get the image geometry that describes the target volume."""
    xDim = array.shape[-1]
    if array.ndim == 2:
        nVoxels = xDim*xDim
        ig = ImageGeometry(
            voxel_num_x = xDim,
            voxel_num_y = xDim,
            voxel_size_x = 1/nVoxels,
            voxel_size_y = 1/nVoxels
        )
    elif array.ndim == 3:
        zDim = array.shape[0]
        nVoxels = xDim*xDim*zDim
        ig = ImageGeometry(
            voxel_num_x = xDim,
            voxel_num_y = xDim,
            voxel_num_z = zDim,
            voxel_size_x = 1/nVoxels,
            voxel_size_y = 1/nVoxels,
            voxel_size_z = 1/nVoxels
        )
    return ig


def clipToCircle(array: np.ndarray):
    """Set values outside the circular printing domain to zero."""
    clipped = array.copy()
    clipped[~getCircleMask(array,order)] = 0
    return clipped

def getCircleMask(array: np.ndarray):
    """Return a boolean mask for the circular printing domain."""
    xDim = array.shape[-1]
    circleY, circleX = np.meshgrid(
            np.linspace(-1,1,xDim),
            np.linspace(-1,1,xDim)
        )
    r = (circleX**2 + circleY**2)
    circleMask2D = np.array(r <= 1**2, dtype=bool)

    if array.ndim == 2:
        return circleMask2D
    elif array.ndim == 3:
        return(np.broadcast_to(circleMask2D, array.shape))
