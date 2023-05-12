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

def check_dot_installed():
    """
    Check if Graphviz's dot is installed correctly in the system

    Returns
    -------
    boolean
        Boolean telling if Graphviz's dot is installed correctly
    """
    import subprocess

    try:
        val = subprocess.run(['dot', '-V'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return val.returncode == 0
    except:
        return False
