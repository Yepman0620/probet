


local historySortListKey = KEYS[1]

if not historySortListKey then
    return redis.error_reply("invalid historySortListKey")
end


local historyHashKey = KEYS[2]

if not historyHashKey then
    return redis.error_reply("invalid historyHashKey")
end

local beginGuessUid = ARGV[1]
local historyNum = tonumber(ARGV[2])


if string.len(beginGuessUid) <= 0 then


    local guessListIds = redis.call("zrevrange",historySortListKey,0,historyNum)

    local resultList = {}
    for i,v in ipairs(guessListIds) do
        resultList[i] = redis.call("hget",historyHashKey,v)
    end

    return resultList

else

    local guessScore = tonumber(redis.call("zscore",historySortListKey,beginGuessUid))
    if guessScore < 0 then
        return redis.error_replay("guess score is less zero")
    else
        local guessListIds = redis.call("zrevrangebyscore",historySortListKey,guessScore - 1,0,"limit",0,historyNum)
        local resultList = {}
        for i,v in ipairs(guessListIds) do

            resultList[i] = redis.call("hget",historyHashKey,v)
        end

        return resultList
    end

end



