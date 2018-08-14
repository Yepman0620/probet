


local msgCenterSortListKey = KEYS[1]

if not msgCenterSortListKey then
    return redis.error_reply("invalid msgCenterSortListKey")
end


local msgCenterHashKey = KEYS[2]

if not msgCenterHashKey then
    return redis.error_reply("invalid msgCenterHashKey")
end


local beginMsgId = ARGV[2]
local limitNum = tonumber(ARGV[3])


if string.len(beginMsgId) <= 0 then

    local msgListIds = redis.call("zrevrange",msgCenterSortListKey,0,limitNum)

    local resultList = {}
    for i,v in ipairs(msgListIds) do
        resultList[i] = redis.call("hget",msgCenterHashKey,v)
    end

    return resultList

else

    local msgScore = tonumber(redis.call("zscore",msgCenterSortListKey,beginMsgId))
    if msgScore < 0 then
        return redis.error_replay("msg score is less zero")
    else
        --2147483648 北京时间是2038/1/19 11:14:8
        local msgListIds = redis.call("zrevrangebyscore",msgCenterSortListKey,msgScore - 1,0,"limit",0,limitNum)
        local resultList = {}
        for i,v in ipairs(msgListIds) do
            resultList[i] = redis.call("hget",msgCenterHashKey,v)
        end

        return resultList
    end
end

