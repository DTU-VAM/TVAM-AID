from dataclasses import dataclass
from cil.framework import ImageData
from cil.optimisation.functions import LeastSquares
from cil.optimisation.operators import LinearOperator
from tvam_aid.target import Target
from tvam_aid.configuration import Thresholds
from tvam_aid.operators.linear_operator import TVAMOperator
from tvam_aid.penalties._utils import _getThresholdTarget
import numpy as np

@dataclass(frozen=True)
class L2N:
    """L2-norm penalties applied to the in-part and out-of-part regions."""
    
    def build(
            self,
            tvamOperator: TVAMOperator,
            target: Target,
            thresholds: Thresholds):
        """Builds the CIL objective function for the L2N approach."""
        thresholdTarget = _getThresholdTarget(target, thresholds)
        return _L2NPenalty(
            tvamOperator.AT, thresholdTarget,
            thresholds, target.regions.external)

class _L2NPenalty(LeastSquares):
    def __init__(
            self,
            A: LinearOperator,
            b: ImageData,
            thresholds: Thresholds,
            externalMask: np.ndarray,
            c: float=1.0,
            weight=None):
        super().__init__(A,b,c,weight)
        self.externalMask = externalMask

    def __call__(self, x):
        y = self.A.direct(x)
        y.subtract(self.b, out = y)

        y.array[self.externalMask] = 0

        if self.weight is None:
            return self.c * y.dot(y)
        else:
            wy = self.weight.multiply(y)
            return self.c * y.dot(wy)

    def gradient(self, x, out=None):
        if out is None:
            out = x * 0.0

        tmp = self.A.direct(x)
        tmp.subtract(self.b , out=tmp)

        tmp.array[self.externalMask] = 0

        if self.weight is not None:
            tmp.multiply(self.weight, out=tmp)
        self.A.adjoint(tmp, out=out)
        out.multiply(self.c * 2.0, out=out)     
        return out
