# TVAM AID

Tomographic Volumetric Additive Manufacturing Adaptive Illumination Design (TVAM AID) is a Python framework for designing and investigating optimisation-based illumination plans for Tomographic Volumetric Additive Manufacturing (TVAM).

TVAM solidifies a photosensitive material by delivering light-energy doses from multiple angles. Designing these doses can be formulated as an optimisation problem: find a non-negative illumination plan that produces a desired energy-dose distribution within the printing volume.

TVAM AID provides an extensible framework for exploring how the objective functions used in this optimisation influence the resulting dose field. It is built on the [Core Imaging Library (CIL)](https://github.com/TomographicImaging/CIL), allowing existing optimisation methods developed for tomographic imaging to be readily applied to TVAM illumination design.

This repository accompanies:

> Nicole Pellizzon, Richard Huber, Jon Spangenberg and Jakob Sauer Jørgensen (2026) <br>
> Systematic Analysis of Penalty-Optimised Illumination Design for Tomographic Volumetric Additive Manufacturing via the Extendable Framework TVAM AID Using the Core Imaging Library. <br>
> Additive Manufacturing. <br>


## Approaches

Three penalty formulations are currently implemented:

- **L2N:** L2-norm penalties centred on prescribed lower and upper dose thresholds.
- **OSP:** one-sided penalties that do not penalise out-of-part doses below the lower threshold or in-part doses above the upper threshold.
- **OSPW(w>0.0):** extends OSP with an additional penalty on high in-part dose. The parameter `w` controls the width of the no-penalty region above the upper threshold.
- **OSPW(w=0.0):** a special case of `OSPW(w>0.0)` that reduces the in-part penalty to an L2-norm and retains a one-sided penalty out-of-part.


## Metrics
TVAM AID currently evaluates three dose-field metrics as described in the accompanying publication:
- **Process Window (PW):** separation between the minimum in-part and maximum out-of-part achieved dose.
- **In-Part Dose-Range (IPDR):** range of achieved dose values within the in-part region.
- **Voxel Error Rate (VER):** the count of out-of-part voxels with a higher achieved dose than the minimum in-part achieved dose, normalised by the number of voxels in the printable region.


## Basic Usage
```python
from tvam_aid import Thresholds, loadTargetGeometry, \
    nonNegativityConstraint, runOptimisation
from tvam_aid.penalties import OSPW
from tvam_aid.operators import createLinearOperator

approach = OSPW(w=0.0)
thresholds = Thresholds(lower=0.7, upper=0.9)

target = loadTargetGeometry("path/to/target.npy")
tvamOperator = createLinearOperator(target)

objective = approach.build(tvamOperator, target, thresholds)
constraint = nonNegativityConstraint()
illuminationPlan, achievedDose = runOptimisation(
    objective,
    constraint,
    target,
    tvamOperator
)
```

The example notebooks below provide further information on the complete optimisation workflow and other functionalities of TVAM AID.


## Examples

The examples folder contains three Jupyter notebooks that demonstrate the principal workflows shown in the publication.

### `01_Approaches.ipynb` - Penalty Approach Demonstration

This notebook is the recommended starting point for new users. It introduces the core TVAM AID workflow: loading a target geometry, constructing the TVAM operator, defining and solving the optimisation problem, evaluating the resulting dose field, and visualising the illumination plan and achieved dose. The notebook can be used to explore how L2N, OSP, OSPW(w>0.0) and OSPW(w=0.0) influence the achieved dose field. 

### `02_Threshold_sweep.ipynb` - Threshold Parameter Sweep

This notebook treats the lower and upper dose thresholds as design parameters and systematically evaluates their influence on commonly used TVAM metrics Process Window (PW), In-Part Dose-Range (IPDR), and Voxel Error Rate (VER).

### `03_Metric_trimming.ipynb` - Metric Sensitivity to Outliers

This notebook begins the investigation into the sensitivity of the metrics to extreme voxel dose values using percentile-trimmed variants of the metrics. Different statistical methods for identifying voxel dose outliers could define updated or novel metrics.

## Hardware

The examples are configured to use an NVIDIA GPU via ASTRA and are computationally intensive, particularly for the 3D example. For 2D problems, the operator can be configured to use the CPU by setting device='cpu' in RunConfig. The 3D parallel-beam projection used here relies on ASTRA's GPU implementation and is therefore not available through the CPU configuration.


## Installation

TVAM AID requires a working installation of CIL with the ASTRA projection plugin. This can be done by running:
```bash
conda install -c conda-forge -c ccpi cil=24.2.0
```
For more information, please see [CIL installation instructions](https://github.com/TomographicImaging/CIL). Note that TVAM AID was developed and the results in the accompanying publication were generated using CIL 24.2.0. Once CIL and ASTRA are available in your active Python environment, then install TVAM AID.

### Standard installation
```bash
git clone https://github.com/DTU-VAM/TVAM-AID.git
cd TVAM-AID
python -m pip install .
```
The package can then be imported from any working directory as shown in [Basic Usage](#Basic-Usage).

### For demonstration notebooks
To be able to run the demonstration notebooks, install TVAM AID as:
```bash
git clone https://github.com/DTU-VAM/TVAM-AID.git
cd TVAM-AID
python -m pip install ".[notebooks]"
```

### For Development
Clone this repository and install TVAM AID in editable mode (recommended when developing new penalties or extending the framework):
```bash
git clone https://github.com/DTU-VAM/TVAM-AID.git
cd TVAM-AID
python -m pip install -e .
```

## Reproducing the Paper Results
The example notebooks provide the workflows used to generate the numerical results presented in the accompanying publication. A figure-by-figure guide, including the required notebook, target geometry, penalty approach and parameters, is provided in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).


## Citation
[To be updated following publication]

If you use TVAM AID in your research, please include citations to **both** the software on Zenodo and the TVAM AID paper:
> N. Pellizzon, R. Huber, J. Spangenberg and J. S. Jørgensen (2026) <br>
> Systematic Analysis of Penalty-Optimised Illumination Design for Tomographic Volumetric Additive Manufacturing via the Extendable Framework TVAM AID Using the Core Imaging Library. <br>
> Additive Manufacturing. <br>
> **DOI:** <br>
> **Code:** https://github.com/

> N. Pellizzon, R. Huber, J. Spangenberg and J. S. Jørgensen (2026) <br>
> Tomographic Volumetric Additive Manufacturing Adaptive Illumination Design (TVAM AID) <br>
> Zenodo [software archive] <br>
> **DOI:** https://doi.org/ <br>
