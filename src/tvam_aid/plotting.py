from cil.utilities.display import show2D
from cil.utilities.jupyter import islicer
from cil.framework import ImageData
from tvam_aid.target import Target
from tvam_aid import Thresholds
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import Normalize, Colormap
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import MaxNLocator
import cmasher as cmr

def showTarget(target: Target):
    """Display the 2D or 3D target."""
    if target.image.array.ndim==2:
        show2D(target.image)
    elif target.image.array.ndim==3:
        display(islicer(target.image, direction=0))

def plotAchievedDose2D(
        achievedDose: ImageData,
        target: Target,
        thresholds: Thresholds):
    """Plot a 2D achieved dose field or 2D slice of an achieved dose field."""
    if achievedDose.ndim != 2:
        raise ValueError('plotAchievedDose2D requires 2D image data.')

    image = achievedDose.array.copy()
    image[target.regions.external] = 0.0
    maxDose = max(1.0, np.amax(image))

    fig, ax = plt.subplots()
    norm = Normalize(vmin=0.0, vmax=1.0)
    im = ax.imshow(image, cmap=cmr.neutral, norm=norm, aspect='equal')
    ax.tick_params(
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )
    cb = fig.colorbar(
        im,
        ax=ax,
        ticks=np.linspace(0.0,1.0,6,endpoint=True),
        location='left'
    )
    cb.set_label('Dose Intensity')

    # add markers on cb-axis indicating thresholds
    # note (-1e-4 offset to handle overlap with major ticks)
    cb.ax.minorticks_on()
    cb.ax.yaxis.set_ticks(
        [thresholds.lower-1e-4,thresholds.upper-1e-4],
        minor=True
    )
    cb.ax.tick_params(
        axis='y',
        which='minor',
        length=5,
        width=2,
        direction='out',
        pad=15
    )
    for i in cb.ax.yaxis.get_ticklines(minor=True):
        i.set_marker('>')

    if maxDose > 1.0:
        highDose = np.ma.masked_where(image<=1.0, image)
        highNorm = Normalize(vmin=1.0, vmax=maxDose)
        ax.imshow(highDose, cmap=cmr.ember_r)
        highMap = ScalarMappable(norm=highNorm, cmap=cmr.ember_r)
        cbHigh = fig.colorbar(highMap, ax=ax, location='right')
        cbHigh.set_label('Dose Inensity >1')

    return fig, ax

def showAchievedDose3D(achievedDose: ImageData):
    display(islicer(achievedDose, direction=0))

def plotHistogram(
        achievedDose: ImageData,
        target: Target,
        thresholds: Thresholds):
    c1 = 'salmon'
    c2 = 'lightsteelblue'

    image = achievedDose.array.copy()
    image[target.regions.external] = 0.0
    maxDose = max(1.0, np.amax(image))

    fig, ax = plt.subplots()
    histBins = np.linspace(0,maxDose,55)
    ax.hist(
        achievedDose.array[target.regions.outPart],
        bins=histBins,
        color=c1,
        alpha=0.5,
        edgecolor='white',
        linewidth=0.3
    )
    ax.hist(
        achievedDose.array[target.regions.inPart],
        bins=histBins,
        color=c2,
        alpha=0.5,
        edgecolor='white',
        linewidth=0.3
    )
    ax.legend(['Out-of-Part', 'In-Part'], loc='upper left')
        
    ax.set_yscale('log')
    ax.set_xlim([0,maxDose])
    ax.set_xlabel('Dose Intensity')
    ax.set_ylabel('Voxel count')

    # add markers on x-axis indicating thresholds
    # note (-1e-4 offset to handle overlap with major ticks)
    ax.minorticks_on()
    ax.xaxis.set_ticks(
        [thresholds.lower-1e-4, thresholds.upper-1e-4],
        minor=True
    )
    ax.tick_params(
        axis='x',
        which='minor',
        length=5,
        width=2,
        direction='out',
        pad=10
    )
    for i in ax.xaxis.get_ticklines(minor=True):
        i.set_marker('^')
    return fig, ax

def plotMetricSensitivity(
        trimmingPercentages: np.ndarray,
        trimmedIPDR: np.ndarray,
        trimmedPW: np.ndarray,
        highlightedPercentage: float=None):
    fig, ax = plt.subplots()
    ax.plot(trimmingPercentages, trimmedIPDR, label='IPDR')
    ax.plot(trimmingPercentages, trimmedPW, label='PW')

    if highlightedPercentage is not None:
        ax.axvline(
            highlightedPercentage,
            linestyle="--",
            label='{}% removed'.format(highlightedPercentage)
        )
    
    ax.set_xlabel('Percentage of each distribution removed')
    ax.set_ylabel('Metric value')
    ax.legend()
    return fig, ax

def plotPWSweep(PW: np.ndarray, thresholdValues: np.ndarray):
    """Plot a Process Window (PW) colour map."""
    tickValues, levels = _getMetricMapTicksAndLevels(PW)
    cmap=cmr.fusion_r
    norm = colors.TwoSlopeNorm(
        vmin=tickValues[0],
        vmax=tickValues[-1],
        vcenter=0.0
    )

    fig, ax, cb = _plotMetricMap(
        PW,
        thresholdValues,
        levels,
        cmap,
        norm
    )
    cb.set_ticks(tickValues)
    cb.set_label('PW')
    return fig, ax

def plotIPDRSweep(IPDR: np.ndarray, thresholdValues: np.ndarray):
    """Plot an In-Part Dose Range (IPDR) colour map."""
    tickValues, levels = _getMetricMapTicksAndLevels(IPDR)
    cmap = cmr.get_sub_cmap(cmr.swamp_r, 0.1, 1.)
    norm = colors.Normalize(vmin=tickValues[0], vmax=tickValues[-1])

    fig, ax, cb = _plotMetricMap(
        IPDR,
        thresholdValues,
        levels,
        cmap,
        norm
    )
    cb.set_ticks(tickValues)
    cb.set_label('IPDR')
    return fig, ax

def plotVERSweep(VER: np.ndarray, thresholdValues: np.ndarray):
    """Plot a Voxel Error Rate (VER) colour map."""
    tickValues, levels = _getMetricMapTicksAndLevels(VER)
    cmap = cmr.get_sub_cmap(cmr.amethyst_r, 0.1, 1.)
    norm = colors.Normalize(vmin=tickValues[0], vmax=tickValues[-1])

    fig, ax, cb = _plotMetricMap(
        VER,
        thresholdValues,
        levels,
        cmap,
        norm
    )
    cb.set_ticks(tickValues)
    cb.set_label('VER')
    return fig, ax

def _getMetricMapTicksAndLevels(metric: np.ndarray):
    locator = MaxNLocator(nbins=5)
    tickValues = locator.tick_values(
        np.nanmin(metric),
        np.nanmax(metric)
    )
    
    vmin = tickValues[0]
    vmax = tickValues[-1]
    levels = np.linspace(vmin, vmax, 101, endpoint=True)
    return tickValues, levels

def _plotMetricMap(
        metric: np.ndarray,
        thresholdValues: np.ndarray,
        levels: np.ndarray,
        cmap: Colormap,
        norm: Normalize):
    fig, ax = plt.subplots()

    image = ax.contourf(
        thresholdValues,
        thresholdValues,
        metric,
        levels=levels,
        cmap=cmap,
        norm=norm
    )
    ax.set_xlabel(r'$\tau_{\rm upper}$')
    ax.set_ylabel(r'$\tau_{\rm lower}$')
    ax.set_xlim([-0.05, 1.05])
    ax.set_ylim([-0.05, 1.05])

    cb = fig.colorbar(image, ax=ax)
    return fig, ax, cb

def plotSliceMetrics(
        achievedDose: ImageData,
        target: Target,
        alphas: list[float]):
    """Plot PW and IPDR on a slice-by-slice basis for a 3D dose field."""
    if achievedDose.ndim != 3:
        raise ValueError('plotSliceMetrics requires 3D image data.')

    if not alphas:
        raise ValueError('alphas must contain at least one value.')

    if any(alpha < 0 or alpha >= 50 for alpha in alphas):
        raise ValueError('Each alpha must be in the range [0, 50).')

    image = achievedDose.array
    nSlices = image.shape[0]
    sliceIndices = np.arange(nSlices)

    # Calculate untrimmed metrics.
    PW = np.empty(nSlices)
    IPDR = np.empty(nSlices)

    for z in sliceIndices:
        inPart = image[z][target.regions.inPart[z]]
        outPart = image[z][target.regions.outPart[z]]

        PW[z] = np.amin(inPart) - np.amax(outPart)
        IPDR[z] = np.amax(inPart) - np.amin(inPart)

    fig, ax = plt.subplots()

    # Untrimmed metrics
    ax.plot(sliceIndices, PW, label='PW')
    ax.plot(sliceIndices, IPDR, label='IPDR')

    # Trimmed metrics
    for alpha in alphas:
        if alpha == 0:
            continue

        trimmedPW = np.empty(nSlices)
        trimmedIPDR = np.empty(nSlices)

        for z in sliceIndices:
            inPart = image[z][target.regions.inPart[z]]
            outPart = image[z][target.regions.outPart[z]]

            inPartLower = np.percentile(inPart, alpha)
            inPartUpper = np.percentile(inPart, 100 - alpha)
            outPartUpper = np.percentile(outPart, 100 - alpha)

            trimmedPW[z] = inPartLower - outPartUpper
            trimmedIPDR[z] = inPartUpper - inPartLower

        pwLabel = rf'$\mathrm{{PW}}_{{{alpha:g}\%}}^{{{100-alpha:g}\%}}$'
        ipdrLabel = rf'$\mathrm{{IPDR}}_{{{alpha:g}\%}}^{{{100-alpha:g}\%}}$'

        ax.plot(sliceIndices, trimmedPW, label=pwLabel)
        ax.plot(sliceIndices, trimmedIPDR, label=ipdrLabel)

    ax.set_xlabel('Slice $z$')
    ax.set_ylabel('Metric value')
    ax.set_xlim(0, nSlices - 1)
    ax.legend()
    return fig, ax
