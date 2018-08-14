

local guessDataKey = KEYS[1]
local guessLockIdKey = KEYS[2]
local guessLockTimeKey = KEYS[3]


local guessId = ARGV[1]
local lockFlag = ARGV[2]
local lockId = ARGV[3]
local lockExpireTime = ARGV[4]


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
local existLockTime = redis.call("get",guessLockTimeKey)

if lockFlag == "True" and existLock and existLockTime then
    return redis.error_reply("guess locked|"..guessId.."|"..existLock)
end

local guessData = redis.call("hget",guessDataKey,guessId)
if guessData and lockFlag == "True" then

    redis.call("set",guessLockIdKey,lockId)
    redis.call("set",guessLockTimeKey,"lock")
    redis.call("pexpire",guessLockTimeKey,lockExpireTime)
    redis.call("expire",guessLockIdKey,3600)
end

return guessData


