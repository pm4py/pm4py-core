import shutil
from enum import Enum
from typing import Optional, Dict, Any

from pm4py.util import exec_utils, vis_utils, constants
from pm4py.visualization.performance_spectrum.variants import neato


class Variants(Enum):
    NEATO = neato


def apply(perf_spectrum: Dict[str, Any], variant=Variants.NEATO, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Construct the performance spectrum visualization

    Parameters
    ----------------
    perf_spectrum
        Performance spectrum
    variant
        Variant of the visualization to use:
        - NEATO: using the Graphviz Neato layouter
    parameters
        Variant-specific parameters

    Returns
    ---------------
    file_path
        Path containing the visualization
    """
    return exec_utils.get_variant(variant).apply(perf_spectrum, parameters=parameters)


def view(figure: str):
    """
    Views the performance spectrum

    Parameters
    ---------------
    figure
        Path containing the visualization
    """
    if constants.DEFAULT_GVIZ_VIEW == "matplotlib_view":
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        img = mpimg.imread(figure)
        plt.axis('off')
        plt.tight_layout(pad=0, w_pad=0, h_pad=0)
        plt.imshow(img)
        plt.show()
        return

    if vis_utils.check_visualization_inside_jupyter():
        vis_utils.view_image_in_jupyter(figure)
    else:
        vis_utils.open_opsystem_image_viewer(figure)


def save(figure: str, output_file_path: str):
    """
    Saves the performance spectrum at the specified path

    Parameters
    ---------------
    figure
        Path containing the visualization
    output_file_path
        Path into which the image should be saved
    """
    shutil.copyfile(figure, output_file_path)


def serialize(figure: str):
    """
    Serializes the performance spectrum visualization

    Parameters
    ---------------
    figure
        Path containing the visualization
    """
    with open(figure, "rb") as f:
        return f.read()


def matplotlib_view(figure: str):
    """
    Views the performance spectrum using Matplotlib

    Parameters
    ---------------
    figure
        Path containing the visualization
    """
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    img = mpimg.imread(figure)
    plt.imshow(img)
    plt.show()
