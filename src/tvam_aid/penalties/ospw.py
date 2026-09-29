from dataclasses import dataclass
from cil.framework import ImageData
from cil.optimisation.functions import LeastSquares
from cil.optimisation.operators import LinearOperator
from tvam_aid.target import Target, VoxelRegions
from tvam_aid.configuration import Thresholds
from tvam_aid.operators.linear_operator import TVAMOperator
from tvam_aid.penalties._utils import _getThresholdTarget
import numpy as np

@dataclass(frozen=True)
class OSPW:
    w: float

    def build(
            self,
            tvamOperator: TVAMOperator,
            target: Target,
            thresholds: Thresholds):
        if self.w == 0.0:
            penalty = _OSPWZeroPenalty
        else:
            penalty = _OSPWPenalty

        thresholdTarget = _getThresholdTarget(target, thresholds)
        return penalty(
            tvamOperator.AT, thresholdTarget,
            thresholds, target.regions,
            self.w
        )

class _OSPWPenalty(LeastSquares):
    def __init__(
            self,
            A: LinearOperator,
            b: ImageData,
            thresholds: Thresholds,
            regions: VoxelRegions,
            w: float,
            c: float=1.0,
            weight=None):
        super().__init__(A,b,c,weight)
        self.tLower = thresholds.lower
        self.tUpper = thresholds.upper
        self.inMask = regions.inPart
        self.outMask = regions.outPart
        self.externalMask = regions.external
        self.w = w

    def __call__(self, x):
        recon = self.A.direct(x)
        y = self.A.direct(x)
        y.subtract(self.b, out = y)

        lessThanLowerThresh = np.array(recon.array <= self.tLower, dtype=bool)
        moreThanUpperThresh = np.array(recon.array >= self.tUpper, dtype=bool)
        lessThanUpperPenalty = np.array(
            recon.array < (self.tUpper + self.w),
            dtype = bool
        )
        
        outerMask = np.logical_and(self.outMask,lessThanLowerThresh)
        y.array[outerMask] = 0

        innerMask = np.logical_and(
            np.logical_and(self.inMask, moreThanUpperThresh),
            lessThanUpperPenalty
        )
        y.array[innerMask] = 0

        y.array[self.externalMask] = 0

        if self.weight is None:
            return self.c * y.dot(y)
        else:
            wy = self.weight.multiply(y)
            return self.c * y.dot(wy)

    def gradient(self, x, out=None):
        if out is None:
            out = x * 0.0

        recon = self.A.direct(x)
        tmp = self.A.direct(x)
        tmp.subtract(self.b , out=tmp)

        lessThanLowerThresh = np.array(recon.array <= self.tLower, dtype=bool)
        moreThanUpperThresh = np.array(recon.array >= self.tUpper, dtype=bool)
        lessThanUpperPenalty = np.array(
            recon.array < (self.tUpper + self.w),
            dtype = bool
        )
        
        outerMask = np.logical_and(self.outMask,lessThanLowerThresh)
        tmp.array[outerMask] = 0

        innerMask = np.logical_and(
            np.logical_and(self.inMask,moreThanUpperThresh),
            lessThanUpperPenalty
        )
        tmp.array[innerMask] = 0

        tmp.array[self.externalMask] = 0
                
        if self.weight is not None:
            tmp.multiply(self.weight, out=tmp)
        self.A.adjoint(tmp, out = out)
        out.multiply(self.c * 2.0, out=out)     
        return out


class _OSPWZeroPenalty(LeastSquares):
    def __init__(
            self,
            A: LinearOperator,
            b: ImageData,
            thresholds: Thresholds,
            regions: VoxelRegions,
            w: float,
            c: float=1.0,
            weight=None):
        super().__init__(A,b,c,weight)
        self.tLower = thresholds.lower
        self.tUpper = thresholds.upper
        self.inMask = regions.inPart
        self.outMask = regions.outPart
        self.externalMask = regions.external
        self.w = w


    def __call__(self, x):
        recon = self.A.direct(x)
        y = self.A.direct(x)
        y.subtract(self.b, out = y)

        lessThanLowerThresh = np.array(recon.array <= self.tLower, dtype=bool)
        
        outerMask = np.logical_and(self.outMask, lessThanLowerThresh)
        y.array[outerMask] = 0

        y.array[self.externalMask] = 0

        if self.weight is None:
            return self.c * y.dot(y)
        else:
            wy = self.weight.multiply(y)
            return self.c * y.dot(wy)

    def gradient(self, x, out=None):
        if out is None:
            out = x * 0.0

        recon = self.A.direct(x)
        tmp = self.A.direct(x)
        tmp.subtract(self.b , out=tmp)

        lessThanLowerThresh = np.array(recon.array <= self.tLower, dtype=bool)
        
        outerMask = np.logical_and(self.outMask,lessThanLowerThresh)
        tmp.array[outerMask] = 0

        tmp.array[self.externalMask] = 0
                
        if self.weight is not None:
            tmp.multiply(self.weight, out=tmp)
        self.A.adjoint(tmp, out = out)
        out.multiply(self.c * 2.0, out=out)     
        return out
