
local guessDataKey = KEYS[1]

if not guessDataKey then
    return redis.error_reply("invalid guessDataKey")
end

--local matchDataList = ARGV[1]

local resultList = {}
for i,v in ipairs(ARGV) do
    resultList[i] = redis.call("hget",guessDataKey,v)
end

return resultList


