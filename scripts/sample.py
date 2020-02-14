from pm4py.objects.process_tree import pt_util

'''
Use the scripts folder to write custom scripts for your (research) project, when using PM4Py directly from source.  
'''


def pm4py_demo_script():
    pt1 = pt_util.parse('X(\'a\',\'b\')')
    print(pt1)


if __name__ == '__main__':
    pm4py_demo_script()
