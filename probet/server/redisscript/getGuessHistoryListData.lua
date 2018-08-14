
local guessHistoryDataKey = KEYS[1]

if not guessHistoryDataKey then
    return redis.error_reply("invalid guessHistoryDataKey")
end

--local matchDataList = ARGV[1]

local resultList = {}
for i,v in ipairs(ARGV) do
    resultList[i] = redis.call("hget",guessHistoryDataKey,v)
end

return resultList


