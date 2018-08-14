from enum import Enum
import sys

class exceptionLogic(Exception):
    def __init__(self,error_info:list,*args,**kwargs):
        super(exceptionLogic,self).__init__(args,kwargs)
        self.iErrorNum = error_info[0]
        self.strMsgDes = error_info[1]
        self.tb = sys.exc_info()[2]

    def __repr__(self):
        return "[{}] [{}] []".format(self.iErrorNum,self.strMsgDes,self.with_traceback(self.tb))

#############################################################################################


class errorLogic(object):

    success = [0,""]

    sys_unknow_error = [1, "网络错误|系统错误"]
    client_param_invalid = [2, "网络错误|输入参数非法"]
    verify_code_expired = [3, "提醒|验证码已失效，请重新获取验证码"]
    verify_code_not_valid = [4, "提醒|验证码不正确，请确认验证码"]
    data_locked = [5, "提醒|网络错误，请稍后再试"]
    type_not_valid = [6, "提醒|请选择正确的类型"]
    data_not_valid = [7, "提醒|数据不存在"]
    user_already_login = [8, "提醒|用户已登陆"]


    ###比赛相关的
    match_data_not_found = [100, "提醒|赛事未找到"]  # 赛事数据没有找到
    match_guess_not_open = [101, "提醒|竞猜未开始"]  # 竞猜数据没开始
    match_guess_not_found = [102, "提醒|竞猜未找到"]  # 竞猜数据没有找到

    guess_bet_num_max_limit = [103, "提醒|最高投注受限,当前你已竞猜{}"]
    guess_bet_num_min_limit = [104, "提醒|竞猜金额最小10元，请重新押注"]

    match_state_close = [110, "提醒|本场比赛已经结束"]
    match_guess_state_close = [111, "提醒|本竞猜项封盘，请留意其他竞猜项"]

    guess_data_not_found = [120, "提醒|竞猜未找到"]


    bet_hist_data_not_found = [130, "竞猜历史数据没找到"]
    bet_his_data_already_back = [131, "竞猜押注已经回退"]
    guess_result_key_not_found = [132, "竞猜结果Key没有找到"]
    guess_return_rate_fix = [133, "返还率已经锁定，不能修改"]
    guess_return_rate_fixUpDownRateFailed_Less1Value = [134, "返还率已经锁定，调整会导致 {} 赔率 小于 1.0"]
    guessInitRate_Less1Value = [135, "赔率 小于 1.0 不合法"]


    ###用户相关的
    player_id_empty = [201, "提醒|未登陆"]  # 用户账号id是空，没有登陆，游客账号吧
    player_data_not_found = [202, "提醒|账号未找到"]  # 用户账号数据未找到
    player_coin_not_enough = [203, "提醒|余额不足"]  # 用户coin不足
    player_id_already_exist = [204, "提醒|账号已存在"]  # 用户的账号id 已经存在
    player_id_invalid = [205, '错误|该账号由于违规被冻结']
    player_drawing_not_enough = [206, "提醒|超出可提额度"]  # 用户可提现额度不足
    player_drawing_coin_not_int = [207, "提醒|需要整数金额"]  # 用户可提现额度不足
    player_token_certify_not_success = [208, "提醒|账号信息过期,请重新登陆"]
    player_reg_limited = [209, "提醒|内测限制注册，如有需要请联系客服人员"]


    login_token_not_valid = [210, "错误|用户信息过期，请重新登陆账号"]  # 用户token不合法
    login_token_expired = [211, "提醒|账号长时间没有登陆，需要重新输入账号密码登陆"]  # 用户token过期
    login_pwd_not_valid = [212, "提醒|账号或密码不正确"]  # 用户密码不正确
    login_only_pwd_not_valid = [213, "提醒|密码不正确"]  # 用户密码不正确
    login_only_old_pwd_not_valid = [214, "提醒|旧密码不正确"]  # 用户密码不正确
    login_pwd_same_old = [215, "提醒|新密码和旧密码相同，请重新设置密码"]  # 用户密码不正确
    login_by_other_device = [216, "提醒|账号在其他设备登陆"]  # 账号在其他设备登陆

    player_id_contain_invalid_char = [217, "提醒|请使用字母开头和数字组合的账号格式"]
    player_pwd_length_out_of_range = [218, "提醒|请使用字母开头和数字组合8-16长度的密码"]
    player_nick_contain_invalid_char = [219, "提醒|昵称含非法字符"]
    player_id_length_out_of_range = [220,"提醒|账号长度请保持6-24，请重新输入"]
    player_telephone_invalid = [221,"提醒|手机号码格式不正确"]
    player_telephone_is_none = [222,"提醒|手机号不能为空，请输入手机号"]
    player_Email_is_none = [223,"提醒|邮箱不能为空，请输入邮箱"]
    player_Email_invalid = [224,"提醒|邮箱格式不正确"]
    player_telephone_is_not_bind = [225, "提醒|该手机号未绑定或不存在"]
    player_Email_is_not_bind = [226, "提醒|该邮箱未绑定或不存在"]
    player_TradePwd_length_out_of_range = [227, "提醒|请使用6位数字的密码"]
    player_pwd_pwd2_not_same = [228, "提醒|两次密码不一致"]
    player_bankcard_max_limit = [229, "提醒|绑定的银行卡已达上限"]

    pay_type_not_valid = [230, "提醒|请选择正确的支付方式"]
    pay_failed = [231, "提醒|充值失败请稍后再试"]
    pay_qrcode_invalid = [232, "提醒|充值二维码已经失效,请重新下单"]
    trade_pwde_not_valid = [233, "提醒|交易密码不正确"]
    trade_pwde_not_bind = [234, "提醒|交易密码不存在"]
    pay_online_amount_limit = [235, "提醒|线上支付最低10元，最高3000"]
    pay_offline_amount_limit = [236, "提醒|线上支付最低30元，最高500000"]
    pay_channel_not_support = [237, "提醒|充值渠道暂时不支持"]


    token_not_valid = [260, "提醒|该账号信息过期,请重新登陆"]
    player_token_not_valid = [261, "提醒|账号信息过期,请重新登陆"]
    player_avator_not_null = [262, "提醒|头像不能为空"]
    player_bank_card_not_valid = [263, "提醒|请输入正确的银行卡号"]
    player_bank_card_not_found = [264,"提醒|用户卡号未找到"]
    code_send_not_success = [265,"提醒|验证码获取失败，请重新获取"]


    active_already_exist = [300, "错误|活动已经存在"]
    active_not_find = [301, "错误|活动未找到"]
    active_cfg_not_find = [302, "错误|活动已经过期,请咨询客服人员"]
    active_have_already_get = [303, "提醒|此类活动已经参与,如有疑问请咨询客服人员"]
    active_award_not_get=[304,"提醒|活动奖金未及时领取，已过期"]
    active_requirements_not_met=[305,"提醒|活动要求未达到，暂不能领取"]
    active_time_not_valid = [306, "提醒|活动时间还没开放或者已经过期，暂不能领取"]

    kick_off_login = [1001,""]
    data_version_not_valid = [1000,"错误|数据版本有误"]
    db_error=[1001,'错误|存储数据失败']
    third_party_error=[1002,'錯誤|第三方接口錯誤']

    ####代理相关
    agent_data_not_found=[240,'提醒|代理账户未找到']
    agent_id_already_exist=[241,'提醒|代理账户已存在']
    user_data_not_found=[242,'提醒|请先成为我们的会员']
    agent_id_under_review=[243,'提醒|账号审核中...']
    user_is_agent=[244,'该用户是代理，不能新增为下线用户']
    user_has_agent=[245,'该用户已经是别的代理的下线，添加失败']

    ####################后台管理错误码
    attributte_cannot_visit=[600,"提醒|属性不能访问"]
    user_permission_denied=[601,"提醒|权限不足"]
    account_already_exists=[602,"提醒|账号已存在"]
    wrong_accountId_or_password=[603,"提醒|用户名或密码错误"]
    only_change_your_pwd=[604,"提醒|只能修改自己的密码"]
    lockTime_or_lockReason_lack=[605,"提醒|冻结账号的时长或原因缺少"]
    please_enter_the_recipient=[606,"提醒|消息接收人缺少"]
    hisCoin_info_not_found=[607,"提醒|流水单号未找到，确认失败"]
    hisCoin_state_not_correct=[608,"提醒|确认到账失败，订单不是等待状态"]
    select_condition_not_valid = [609, "提醒|请输入查询条件"]
    user_account_format_not_valid = [610, "提醒|管理端账号有非法字符，请重新填写"]
    third_deductions_failed=[611,"扣款失败"]
    not_cancel_reason=[612,"取消原因未填写"]
    recovery_data_failed=[613,"恢复数据失败"]

    ###########平博错误码
    pinbo_error_code={"103":"Your player's account has been <status>. 您用户的账号已经被注册",
                      "104":"Member not exist in system.系统没有这个用户",
                      '105':"User create fail. 创建用户失败 ",
                      "106":"User locked by login fail many times.登录失败多次账号被锁",
                      "107":"Agent hasn't key store in system. 代理系统里没有储存 key",
                      "108":"Agent invalid.Please contact partner to get agent code.代理码无效。请联系合作伙伴获取代理码",
                      "109":"You don't allow create player under agent code who is not directly down line.您不允许在不直接下线的代理商代码下创建播放器。",
                      "110":"Agent not exist in system.系统没有这个代理",
                      "111":"Login id ready exist in system.登录名在系统里已存在",
                      "112":"Login id is not valid.登录名无效",
                      "113":"User's brand is not support login. 客户品牌不支持登陆",
                      "114":"Cannot change status when user is Closed or Suspended by Company.如果用户的账号被公司关闭或暂停，不可以更改状态",
                      "115":"User account hasn't exist in system. 用户账号在系统里不存在",
                      "305":"Player has no permission create key store.用户没有权限创建 key store",
                      "306":"Invalid parameters.You will have information in message of error.无效的参数。你将有错误信息的消息。",
                      "307":"Account Balance do not exist in system.帐户余额在系统不存在。 ",
                      "308":"Your amount should be a positive number 你的金额应该是一个正数",
                      "309":"Your balance is not enough.你的余额不足。",
                      "310":"Your balance exceeded credit limit.你的余额超过了信用额度",
                      "311":"Amount value should be two decimal places.金额值应该是小数点后两位。",
                      "403":"The token for this brand is still not generated.这个品牌的代码还没有产生。",
                      "405":"Your wallet do not exist in system.你的钱包在系统不存在。",
                      "406":"Your wallet is inactive.你的钱包是不活跃",
                      "407":"Invalid product.产品无效。",
                      "423":"Your account is < status >.Please contact your up line for help.您的帐户是 < 状态 >。请联系您的上线寻求 帮助",
                      }

