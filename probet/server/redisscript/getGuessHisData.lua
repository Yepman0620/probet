
local guessHisDataKey = KEYS[1]
local guessHisLockIdKey = KEYS[2]
local guessHisLockTimeKey = KEYS[3]


local guessHisUId = ARGV[1]
local lockFlag = ARGV[2]
local lockId = ARGV[3]
local lockExpireTime = ARGV[4]


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
local existLockTime = redis.call("get",guessHisLockTimeKey)

if lockFlag == "True" and existLock and existLockTime then
    return redis.error_reply("guessHis locked|"..guessHisUId.."|"..existLock)
end

local guessHisData = redis.call("hget",guessHisDataKey,guessHisUId)
if guessHisData and lockFlag == "True" then

    redis.call("set",guessHisLockIdKey,lockId)
    redis.call("set",guessHisLockTimeKey,"lock")
    redis.call("pexpire",guessHisLockTimeKey,lockExpireTime)
    redis.call("expire",guessHisLockIdKey,3600)
end

return guessHisData
