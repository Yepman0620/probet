


local sortListKey = KEYS[1]

if not sortListKey then
    return redis.error_reply("invalid sortListKey")
end


local matchDataKey = KEYS[2]

if not matchDataKey then
    return redis.error_reply("invalid matchDataKey")
end

local matchDataId = ARGV[1]
local matchNum = tonumber(ARGV[2])

local matchIdIndex = 0



matchIdIndex = 0
local nowTime = redis.call("Time")

local matchListIds = redis.call("zrevrangebyrank",sortListKey,nowTime[1] + 8640000,nowTime[1])

local resultList = {}
for i,v in ipairs(matchFutureListIds) do
    resultList[i] = redis.call("hget",matchDataKey,v)
end


return resultList



