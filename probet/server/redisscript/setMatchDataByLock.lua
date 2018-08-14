
local matchDataKey = KEYS[1]
local matchLockIdKey = KEYS[2]
local matchLockTimeKey = KEYS[3]
local matchDataKey_dirty = KEYS[4]



local matchId = ARGV[1]
local MatchBytes = ARGV[2]
local lockId = ARGV[3]


if not matchDataKey then
    return redis.error_reply("invalid matchDataKey")
end


if not matchLockIdKey then
    return redis.error_reply("invalid matchLockIdKey")
end

if not matchLockTimeKey then
    return redis.error_reply("matchLockTimeKey")
end


local existLock = redis.call("get",matchLockIdKey)

if existLock and lockId ~= existLock then
    return redis.error_reply("lock id not same")
end


redis.call("hset",matchDataKey,matchId,MatchBytes)
redis.call("del",matchLockIdKey)
redis.call("del",matchLockTimeKey)

redis.call("sadd", matchDataKey_dirty,matchId)
