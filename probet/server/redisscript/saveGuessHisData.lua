
local guessHisDataKey = KEYS[1]
local guessHisLockIdKey = KEYS[2]
local guessHisLockTimeKey = KEYS[3]
local guessHisDataKey_dirty = KEYS[4]


local guessHisUId = ARGV[1]
local guessHisBytes = ARGV[2]
local lockId = ARGV[3]


if not guessHisDataKey then
    return redis.error_reply("invalid guessHisDataKey")
end


if not guessHisLockIdKey then
    return redis.error_reply("invalid guessHisLockIdKey")
end

if not guessHisLockTimeKey then
    return redis.error_reply("guessHisLockTimeKey")
end


local existLock = redis.call("get",guessHisLockIdKey)

if existLock and lockId ~= existLock then
    return redis.error_reply("lock id not guessHis")
end

redis.call("hset",guessHisDataKey,guessHisUId,guessHisBytes)
redis.call("sadd",guessHisDataKey_dirty,guessHisUId)
redis.call("del",guessHisLockIdKey)
redis.call("del",guessHisLockTimeKey)

