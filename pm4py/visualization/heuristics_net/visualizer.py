'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import shutil
from enum import Enum

import pydotplus
from pm4py.util import exec_utils, vis_utils
from pm4py.visualization.heuristics_net.variants import pydotplus_vis
import tempfile
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from typing import Optional, Dict, Any
from pm4py.util import constants


class Variants(Enum):
    PYDOTPLUS = pydotplus_vis


DEFAULT_VARIANT = Variants.PYDOTPLUS


def apply(heu_net: HeuristicsNet, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> str:
    """
    Gets a representation of an Heuristics Net

    Parameters
    -------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm, including:
            - Parameters.FORMAT
    variant
        Variant of the algorithm to use:
             - Variants.PYDOTPLUS

    Returns
    ------------
    gviz
        Representation of the Heuristics Net
    """
    return exec_utils.get_variant(variant).apply(heu_net, parameters=parameters)


def get_graph(heu_net: HeuristicsNet, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> pydotplus.graphviz.Dot:
    """
    Gets a representation of an Heuristics Net

    Parameters
    -------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm, including:
            - Parameters.FORMAT
    variant
        Variant of the algorithm to use:
             - Variants.PYDOTPLUS

    Returns
    ------------
    graph
        Pydotplus graph
    """
    return exec_utils.get_variant(variant).get_graph(heu_net, parameters=parameters)


def view(figure):
    """
    View on the screen a figure that has been rendered

    Parameters
    ----------
    figure
        figure
    """
    try:
        filename = figure.name
        figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

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


def save(figure, output_file_path):
    """
    Save a figure that has been rendered

    Parameters
    -----------
    figure
        figure
    output_file_path
        Path where the figure should be saved
    """
    try:
        filename = figure.name
        figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

    shutil.copyfile(figure, output_file_path)


def serialize(figure: tempfile._TemporaryFileWrapper) -> bytes:
    """
    Serialize a figure that has been rendered

    Parameters
    ----------
    figure
        figure
    """
    with open(figure.name, "rb") as f:
        return f.read()


def matplotlib_view(figure):
    """
    Views the figure using Matplotlib

    Parameters
    ---------------
    figure
        Figure
    """
    try:
        filename = figure.name
        figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    img = mpimg.imread(figure)
    plt.imshow(img)
    plt.show()
