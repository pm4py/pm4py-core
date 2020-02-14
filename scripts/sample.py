from pm4py.objects.process_tree import pt_util

'''
Use the scripts folder to write custom scripts for your (research) project, when using PM4Py directly from source.  
'''


def pm4py_demo_script():
    pt1 = pt_util.parse('->(\'a\',\'b\')')
    pt2 = pt_util.parse('->(\'a\',\'b\')')
    pt3 = pt_util.parse('X(\'b\',->(\'a\',->(\'a\', X(\'b\', tau))))')

    print(pt1 == pt2)
    print(pt2 == pt3)
    print(pt1 == pt3)
    print(hash(pt1))
    print(hash(pt2))
    print(hash(pt3))


if __name__ == '__main__':
    pm4py_demo_script()
