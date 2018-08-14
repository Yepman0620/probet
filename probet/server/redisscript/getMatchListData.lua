
local matchDataKey = KEYS[1]

if not matchDataKey then
    return redis.error_reply("invalid matchDataKey")
end

--local matchDataList = ARGV[1]

local resultList = {}
for i,v in ipairs(ARGV) do
    resultList[i] = redis.call("hget",matchDataKey,v)
end

return resultList


