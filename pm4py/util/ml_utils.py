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
import importlib.util


def DecisionTreeClassifier(*args, **kwargs):
    from sklearn.tree import DecisionTreeClassifier

    return DecisionTreeClassifier(*args, **kwargs)


def AffinityPropagation(*args, **kwargs):
    from sklearn.cluster import AffinityPropagation

    return AffinityPropagation(*args, **kwargs)


def KMeans(*args, **kwargs):
    from sklearn.cluster import KMeans

    return KMeans(*args, **kwargs)


def KNeighborsRegressor(*args, **kwargs):
    from sklearn.neighbors import KNeighborsRegressor

    return KNeighborsRegressor(*args, **kwargs)


def LocallyLinearEmbedding(*args, **kwargs):
    from sklearn.manifold import LocallyLinearEmbedding

    return LocallyLinearEmbedding(*args, **kwargs)
