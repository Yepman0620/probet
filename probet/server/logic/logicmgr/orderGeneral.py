
import uuid


def generalOrderId():

    '''
    iNowTime = timeHelp.getNow()
    strPreFix = timeHelp.timestamp2Str(iNowTime,"%Y%m%d%H%M%S")

    if g_general_order_id_change_time == iNowTime:
        raise exceptionLogic(errorName.player_id_general_limited.value)

    id = ((iNowTime - 1498674993) << (16 + 8 + 8)) + (procVariable.work_id << (16 + 8))\
         + (procVariable.group_id <<(16)) + g_general_order_id_num

    g_general_order_id_num += 1
    if g_general_order_id_num >= 65535:
        g_general_order_id_num = 0
        g_general_order_id_change_time = iNowTime

    strOrderId = strPreFix + '_' + str(id)
    '''
    return str(uuid.uuid1())


if __name__ == "__main__":
    print(generalOrderId())