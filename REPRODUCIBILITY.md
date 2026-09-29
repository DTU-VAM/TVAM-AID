# Reproducing the Paper Results

The example notebooks in `examples/` demonstrate the workflows used to generate the numerical results presented in the accompanying publication:

> N. Pellizzon, R. Huber, J. Spangenberg and J. S. Jørgensen (2026) <br>
> Systematic Analysis of Penalty-Optimised Illumination Design for Tomographic Volumetric Additive Manufacturing via the Extendable Framework TVAM AID Using the Core Imaging Library. <br>
> Additive Manufacturing. <br>

The notebooks are intended both as examples of the TVAM AID workflow and as the basis for reproducing the results in the paper. The sections below map the principal paper results to the corresponding example notebook and identify the parameters that should be changed where required.

The published calculations were performed using CIL 24.2.0. Exact reproduction should therefore use the same CIL version. The reproducibility scope of this repository is limited to the results generated using TVAM AID. The OSMO results used for comparison in the paper were generated separately using VAMToolbox and are not reproduced here.

The examples are organised into three workflows:
1. `01_Approaches.ipynb` demonstrates optimisation of an individual target using the available penalty approaches,
2. `02_Threshold_sweep.ipynb` demonstrates the threshold-parameter sweep used to investigate the influence of the lower and upper thresholds,
3. `03_Metric_trimming.ipynb` demonstrates the 3D gyroid calculation and the investigation of percentile-trimmed metrics.


## Figure 4 - Comparison of Penalty Functions

**Notebook:** `01_Approaches.ipynb`

**Target:** DTU logo

**Approach:** L2N, OSP, OSPW($w=0.1$), OSPW($w=0.0$)

**Thresholds:** `lower = 0.70`, `upper = 0.90`

**Iterations:** 1000

Run the notebook once for each of the four approaches:

| Figure | Approach | `w` |
| --- | --- | ---: |
| 4a | L2N | — |
| 4b | OSP | — |
| 4c | OSPW | 0.1 |
| 4d | OSPW | 0.0 |

The resulting achieved-dose fields and histograms correspond to Figure 4. The PW and IPDR values from these results are those shown in Figure 5.


## Figure 6 - OSPW($w=0.0$) Threshold Sweep

**Notebook:** `02_Threshold_sweep.ipynb`

**Target:** DTU logo

**Approach:** OSPW($w=0.0$)

**Iterations:** 1000

The notebook performs the threshold sweep over the 325 threshold pairs used in the paper and produces the IPDR, PW and VER metric maps. The same threshold pairs can be defined by:
```python
thresholdValues = np.linspace(0.0, 1.0, num=26, endpoint=True)
thresholdPairs = [
    (i, j, Thresholds(lower=lower, upper=upper))
    for i, lower in enumerate(thresholdValues)
    for j, upper in enumerate(thresholdValues)
    if (lower < upper) and (lower < 1.0) and (upper > 0.0)
]
```
as shown in Section 4 of `02_Threshold_sweep.ipynb`.

The default result uses thresholds:
`lower = 0.70`, `upper = 0.90`,
and the PW-optimal result uses thresholds:
`lower = 0.72`, `upper = 0.96`.

Notes: the threshold sweep is computationally expensive and is not expected to be re-run routinely. The notebook demonstrates the calculation and can be used to reproduce the published sweep given sufficient computational resources.

Individual achieved-dose fields can be generated using `01_Approaches.ipynb`.


## Figures 8 and 9 - OSPW($w=0.0$) Additional 2D Geometry Threshold Sweeps

**Notebook:** `02_Threshold_sweep.ipynb`

**Target:** Disk, Resolution

**Approach:** OSPW($w=0.0$)

**Iterations:** 1000

The same threshold-sweep workflow as described for Figure 6 is applied to the disk and resolution targets. Also as before, individual achieved-dose fields can be generated using `01_Approaches.ipynb`.


## Figures 12, 14 and 15 - 3D Gyroid OSPW($w=0.0$) and Metric Trimming

**Notebook:** `03_Metric_trimming.ipynb`

**Target:** Gyroid

**Approach:** OSPW($w=0.0$)

**Thresholds:** `lower = 0.70`, `upper = 0.90`

**Iterations:** 1500

Figure 12 is reproduced by running the 3D optimisation in Sections 3–4 of the notebook. The resulting achieved-dose field is used to generate the full-volume histogram and the representative x-y slices at `z = [14, 107, 197]`. The achieved dose field and histogram can equally be generated using `01_Approaches.ipynb`.

Figures 14 and 15 use the same achieved-dose field to investigate the sensitivity of PW and IPDR to extreme dose values. Figure 14 is reproduced by the metric-trimming analysis in Section 6. The value highlighted in the paper corresponds to a total of 0.05% of each distribution being excluded, i.e. 0.025% from each tail. Figure 15 is reproduced by the slice-wise analysis in Section 7. PW and IPDR are calculated independently for each x-y slice, both without trimming and with the same 0.05% total trimming used in Figure 14.

## Figure 16 - 3D Gyroid OSPW($w=0.1$)

**Notebook:** `01_Approaches.ipynb`

**Target:** Gyroid

**Approach:** OSPW($w=0.1$)

**Thresholds:** `lower = 0.70`, `upper = 0.90`

**Iterations:** 1500

Figure 16 is reproduced using `01_Approaches.ipynb` by changing the OSPW width from `w = 0.0` to `w = 0.1`. Alternatively, the achieved-dose field and histogram can be generated using Sections 1-4 (inclusive) of `03_Metric_trimming.ipynb` with the same target, thresholds, approach and iteration count.

## Figures A1-A3 - Appendix 2D Geometry Threshold Sweeps

**Notebook:** `02_Threshold_sweep.ipynb`

**Target:** Disk, DTU Logo, Resolution

**Approach:** L2N, OSP, OSPW($w=0.1$), OSPW($w=0.0$)

**Iterations:** 1000

These figures use the same threshold-sweep workflow as Figure 6, changing the target geometry and penalty approach as required.