from cil.optimisation.functions import Function, IndicatorBox
from cil.optimisation.algorithms import FISTA
from tvam_aid.target import Target
from tvam_aid.operators import TVAMOperator
from tvam_aid.configuration import RunConfig
import numpy as np

def nonNegativityConstraint():
    return(IndicatorBox(lower=0.0, upper=np.inf))

def runOptimisation(
        objective: Function,
        constraint: IndicatorBox,
        target: Target,
        tvamOperator: TVAMOperator,
        config: RunConfig = None,
        callbacks: list = []):
    """Solve the TVAM optimisation problem and return the illumination plan and achieved dose."""
    if config is None:
        config = RunConfig()
        
    sinogram = tvamOperator.A.direct(target.image)
    initialIlluminationPlan = sinogram.geometry.allocate()
    
    optimisation = FISTA(
        f = objective,
        g = constraint,
        initial = initialIlluminationPlan,
        max_iteration = config.numIters,
    )
    
    optimisation.run(config.numIters, callbacks=callbacks)
    
    illuminationPlan = optimisation.solution
    achievedDose = tvamOperator.AT.direct(illuminationPlan)

    return illuminationPlan, achievedDose
