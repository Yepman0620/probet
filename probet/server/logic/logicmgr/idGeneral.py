from lib.timehelp import timeHelp
from error.errorCode import exceptionLogic,errorLogic
g_general_short_id_num = 0
g_general_short_id_change_time = 0


def generalShortId():
    global g_general_short_id_num
    global g_general_short_id_change_time
    iNowTime = timeHelp.getNow()

    if g_general_short_id_change_time == iNowTime:
        raise exceptionLogic(errorLogic.player_id_general_limited)


    id = ((iNowTime - 1498674993)<< (16)) + g_general_short_id_num

    g_general_short_id_num+=1
    if g_general_short_id_num >= 65535:
        g_general_short_id_num = 0
        g_general_short_id_change_time = iNowTime

    return id

