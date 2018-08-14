
local spopKey = KEYS[1]
local zaddKey = KEYS[2]

local popId = redis.call("pop",spopKey)

if popId then
    redis.call("sadd",zaddKey,popId)
end

return popId