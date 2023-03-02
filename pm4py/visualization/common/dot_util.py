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
