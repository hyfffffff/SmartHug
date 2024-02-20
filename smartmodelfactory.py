from smartgptmodel import SmartGptModel
from smartbaidumodel import SmartBaiduModel
from smartlocalmodel import SmartLocalModel
from smartglmmodel import SmartGlmModel
from smartglmlocalmodel import SmartGlmLocalModel
from smartxversemodel import SmartXVerseModel

def modelfactory(modelid):
    if modelid == 0:
        model = SmartGptModel()
    elif modelid == 1:
        model = SmartBaiduModel()
    elif modelid == 2:
        model = SmartLocalModel()
    elif modelid == 3:
        model = SmartGlmModel()
    elif modelid == 4:
        model = SmartGlmLocalModel()
    elif modelid == 5:
        model = SmartXVerseModel()
    else:
        model = SmartGlmModel()

    return model
    



