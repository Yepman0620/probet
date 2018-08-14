
local guessDataKey = KEYS[1]
local guessLockIdKey = KEYS[2]
local guessLockTimeKey = KEYS[3]
local guessDataDirtyKey = KEYS[4]

local guessId = ARGV[1]
local guessBytes = ARGV[2]
local lockId = ARGV[3]

if not guessDataKey then
    return redis.error_reply("invalid guessDataKey")
end


if not guessLockIdKey then
    return redis.error_reply("invalid guessLockIdKey")
end

if not guessLockTimeKey then
    return redis.error_reply("guessLockTimeKey")
end


local existLock = redis.call("get",guessLockIdKey)

if existLock and lockId ~= existLock then
    return redis.error_reply("lock id not guess")
end

redis.call("hset",guessDataKey,guessId,guessBytes)
redis.call("del",guessLockIdKey)
redis.call("del",guessLockTimeKey)

redis.call("sadd", guessDataDirtyKey,guessId)

