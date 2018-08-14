

local sortListKey = KEYS[1]

if not sortListKey then
    return redis.error_reply("invalid sortListKey")
end


local matchDataKey = KEYS[2]

if not matchDataKey then
    return redis.error_reply("invalid matchDataKey")
end

local beginIndex = tonumber(ARGV[1])
local endIndex = tonumber(ARGV[2])

local matchFutureListIds = redis.call("zrevrange",sortListKey,beginIndex,endIndex)

local resultList = {}
for i,v in ipairs(matchFutureListIds) do
    resultList[i] = redis.call("hget",matchDataKey,v)
end

return resultList
