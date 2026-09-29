from dataclasses import dataclass
from cil.plugins.astra.operators import ProjectionOperator
from cil.optimisation.operators import LinearOperator
from cil.framework import ImageData, AcquisitionGeometry
from tvam_aid.target import Target
from tvam_aid.configuration import RunConfig

@dataclass(frozen=True)
class TVAMOperator:
    """TVAM forward and adjoint linear operators."""
    A: LinearOperator
    AT: LinearOperator
    
def createLinearOperator(target: Target, config: RunConfig = None):
    """Create a TVAM linear forward operator and its adjoint."""
    if config is None:
        config = RunConfig()
        
    acquisitionGeometry = _getAcquisitionGeometry(target, config)

    A = ProjectionOperator(
        target.image.geometry,
        acquisitionGeometry,
        config.device
    )
    
    # get dominant eigenvalue with smaller tolerance
    eigA = A.PowerMethod(
        A,
        tolerance=1e-20,
        return_all=False,
        method='auto'
    )
    A.set_norm(eigA)
    
    # create adjoint operator 
    AT = AdjointOperator(A)
    eigT = AT.PowerMethod(
        AT,
        max_iteration=10,
        initial=None,
        tolerance=1e-12,
        return_all=False,
        method='auto'
    )
    AT.set_norm(eigT)

    return TVAMOperator(A, AT)

def _getAcquisitionGeometry(target: Target, config: RunConfig):
    """Get the parallel-beam acquisition geometry that descrives the target dimensionality and spatial discretisation."""
    xDim = target.image.shape[-1]
    if target.image.ndim == 2:
        nVoxels = xDim*xDim

        ag = AcquisitionGeometry.create_Parallel2D()\
            .set_angles(config.angles)\
            .set_panel(xDim, pixel_size=1/nVoxels)
    elif target.image.ndim == 3:
        zDim = target.image.shape[0]
        nVoxels = xDim*xDim*zDim

        ag = AcquisitionGeometry.create_Parallel3D()\
            .set_angles(config.angles)\
            .set_panel([xDim,zDim], pixel_size=1/(nVoxels))\
            .set_labels(['vertical', 'angle', 'horizontal'])

    return ag

class AdjointOperator(LinearOperator):
    """
    Defines a new linear operator that swaps the operations of a given linear operator, e.g. for given linear operator $A$, the adjoint operator $B$ has operations $B = A^T$ and $B^T = A$.

    Parameters
    ----------

    operator : A linear operater 
    """
    
    def __init__(self, operator: LinearOperator):
        super().__init__(
            domain_geometry=operator.range_geometry(), 
            range_geometry=operator.domain_geometry()
        )         
        self.operator = operator
                
    def direct(self, x, out=None):
        return self.operator.adjoint(x, out=out)
        
    def adjoint(self, x, out=None):
        return self.operator.direct(x, out=out)
