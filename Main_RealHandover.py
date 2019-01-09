'''
Created on Oct 26, 2018

@author: majid
'''
from pm4py.objects.log.importer import xes as xes_importer
from SN.Utilities import Utilities
from SN.SNCreator import SNCreator

log = xes_importer.factory.import_log("C:\\running-example.xes", parameters= {'timestamp_sort': 'True'})

utils = Utilities(log)



# snFull_DF_hashed, resourceList, activityListHashed = utils.create_full_matrixHashed()
snFull_DF_hashed, resourceList, activityList = utils.create_full_matrix()

# snFull_DF_Enc, resourceList_Enc = utils.resourceEncryption(snFull_DF_hashed)     #ECS


snFull_DF_hashed.to_csv("ListFullReal.csv", sep=',', encoding='utf-8')
# snFull_DF_Enc.to_csv("ListFullRealEnc.csv", sep=',', encoding='utf-8')


# snCrtFull = SNCreator(resourceList_Enc, activityListHashed , snFull_DF_Enc)
# snCrtFull = SNCreator(resourceList, activityListHashed , snFull_DF_hashed)
snCrtFull = SNCreator(resourceList, activityList , snFull_DF_hashed)


RscRscMatrix_handover = snCrtFull.makeRealHandoverMatrix(0)


# resourceList_Dec = utils.resourceDecryption(resourceList_Enc)
# snCrtBasic.setResourceList(resourceList_Dec)


# snCrtBasic.drawRscRscGraph_simple(RscRscMatrix_handover, 0, False)

snCrtFull.drawRscRscGraph_advanced(RscRscMatrix_handover,0, True)

