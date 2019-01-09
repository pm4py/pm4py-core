'''
Created on Oct 26, 2018

@author: majid
'''
from pm4py.objects.log.importer import xes as xes_importer
from SN.Utilities import Utilities
from SN.SNCreator import SNCreator
import pandas as pd

log = xes_importer.factory.import_log("C:\\running-example.xes", parameters= {'timestamp_sort': 'True'})

utils = Utilities(log)



snBasic_DF, resourceList = utils.create_basic_matrix()                  #ICS
# snBasic_DF_Enc, resourceList_Enc = utils.resourceEncryption(snBasic_DF)     #ECS


snBasic_DF.to_csv("ListBasic.csv", sep=',', encoding='utf-8')
# snBasic_DF_Enc.to_csv("ListBasicEnc.csv", sep=',', encoding='utf-8')


# snCrtBasic = SNCreator(resourceList_Enc, [] , snBasic_DF_Enc)
snCrtBasic = SNCreator(resourceList, [] , snBasic_DF)


RscRscMatrix_handover = snCrtBasic.makeHandoverMatrix()

RscRscMatrix_handover_org = pd.DataFrame(RscRscMatrix_handover, index=resourceList, columns=resourceList)
RscRscMatrix_handover_org.to_csv("RscRscMatrix_handover.csv", sep=',', encoding='utf-8')


# resourceList_Dec = utils.resourceDecryption(resourceList_Enc)
# snCrtBasic.setResourceList(resourceList_Dec)


# snCrtBasic.drawRscRscGraph_simple(RscRscMatrix_handover, 0, False)

snCrtBasic.drawRscRscGraph_advanced(RscRscMatrix_handover,0, True)

