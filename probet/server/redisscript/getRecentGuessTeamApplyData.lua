


local guessTeamApplySortListKey = KEYS[1]

if not guessTeamApplySortListKey then
    return redis.error_reply("invalid guessTeamApplySortListKey")
end


local guessTeamApplyHashKey = KEYS[2]

if not guessTeamApplyHashKey then
    return redis.error_reply("invalid guessTeamApplyHashKey")
end


local beginApplyId = ARGV[2]
local limitNum = tonumber(ARGV[3])


if string.len(beginApplyId) <= 0 then

    local appListIds = redis.call("zrevrange",guessTeamApplySortListKey,0,limitNum)

    local resultList = {}
    for i,v in ipairs(appListIds) do
        resultList[i] = redis.call("hget",guessTeamApplyHashKey,v)
    end

    return resultList

else

    local msgScore = tonumber(redis.call("zscore",guessTeamApplySortListKey,beginApplyId))
    if msgScore < 0 then
        return redis.error_replay("guess apply score is less zero")
    else
        --2147483648 北京时间是2038/1/19 11:14:8
        local appListIds = redis.call("zrevrangebyscore",guessTeamApplySortListKey,msgScore - 1,0,"limit",0,limitNum)
        local resultList = {}
        for i,v in ipairs(appListIds) do
            resultList[i] = redis.call("hget",guessTeamApplyHashKey,v)
        end

        return resultList
    end

end