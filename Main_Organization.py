'''
Created on Oct 26, 2018

@author: majid
'''

from pm4py.objects.log.importer import xes as xes_importer
from SN.Utilities import Utilities
from SN.SNCreator import SNCreator


# log = xes_importer.factory.import_log(r'BPI Challenge 2017.xes', parameters= {'timestamp_sort': 'True'})
log = xes_importer.factory.import_log("C:\\running-example.xes", parameters= {'timestamp_sort': 'True'})

utils = Utilities(log)


snFull_DF, resourceList, activityList = utils.create_full_matrix()



snFull_DF.to_csv("ListFull.csv", sep=',', encoding='utf-8')


snCrt_Full = SNCreator(resourceList, activityList, snFull_DF)



ActivityRscMatrix = snCrt_Full.makeActivityRscMatrix() 

RscActMatrix_jointactivities = snCrt_Full.makeJointActivityMatrix() 


# RscRscMatrix_jointactivities = snCrt_Full.convertRscAct2RscRsc(RscActMatrix_jointactivities, "pearson")
RscRscMatrix_jointactivities = snCrt_Full.convertRscAct2RscRsc(RscActMatrix_jointactivities, "pearson")


# snCrt_Full.drawActivityResourceGraph_advanced(ActivityRscMatrix,0, False, True)
snCrt_Full.drawRscRscGraph_advanced(RscRscMatrix_jointactivities, 0.5, False)



