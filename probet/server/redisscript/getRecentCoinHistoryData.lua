


local historySortListKey = KEYS[1]

if not historySortListKey then
    return redis.error_reply("invalid historySortListKey")
end


local historyHashKey = KEYS[2]

if not historyHashKey then
    return redis.error_reply("invalid historyHashKey")
end

local beginOrderId = ARGV[1]
local historyNum = tonumber(ARGV[2])


if string.len(beginOrderId) <= 0 then


    local coinListIds = redis.call("zrevrange",historySortListKey,0,historyNum)

    local resultList = {}
    for i,v in ipairs(coinListIds) do
        resultList[i] = redis.call("hget",historyHashKey,v)
    end

    return resultList

else

    local coinScore = tonumber(redis.call("zscore",historySortListKey,beginOrderId))
    if coinScore < 0 then
        return redis.error_replay("coin score is less zero")
    else
        local coinListIds = redis.call("zrevrangebyscore",historySortListKey,coinScore - 1,0,"limit",0,historyNum)
        local resultList = {}
        for i,v in ipairs(coinListIds) do

            resultList[i] = redis.call("hget",historyHashKey,v)
        end

        return resultList
    end

end



