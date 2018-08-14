


local guessTeamMemberSortListKey = KEYS[1]

if not guessTeamMemberSortListKey then
    return redis.error_reply("invalid guessTeamMemberSortListKey")
end


local guessTeamMemberHashKey = KEYS[2]

if not guessTeamMemberHashKey then
    return redis.error_reply("invalid guessTeamMemberHashKey")
end


local beginMemberId = ARGV[2]
local limitNum = tonumber(ARGV[3])


if string.len(beginMemberId) <= 0 then

    local appListIds = redis.call("zrevrange",guessTeamMemberSortListKey,0,limitNum)

    local resultList = {}
    for i,v in ipairs(appListIds) do
        resultList[i] = redis.call("hget",guessTeamMemberHashKey,v)
    end

    return resultList

else

    local msgScore = tonumber(redis.call("zscore",guessTeamMemberSortListKey,beginMemberId))
    if msgScore < 0 then
        return redis.error_replay("guess member score is less zero")
    else
        --2147483648 北京时间是2038/1/19 11:14:8
        local appListIds = redis.call("zrevrangebyscore",guessTeamMemberSortListKey,msgScore - 1,0,"limit",0,limitNum)
        local resultList = {}
        for i,v in ipairs(appListIds) do
            resultList[i] = redis.call("hget",guessTeamMemberSortListKey,v)
        end

        return resultList
    end

end