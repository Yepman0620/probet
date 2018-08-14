

local matchDataKey = KEYS[1]
local matchLockIdKey = KEYS[2]
local matchLockTimeKey = KEYS[3]


local matchId = ARGV[1]
local lockFlag = ARGV[2]
local lockId = ARGV[3]
local lockExpireTime = ARGV[4]


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
local existLockTime = redis.call("get",matchLockTimeKey)

if lockFlag == "True" and existLock and existLockTime then
    return redis.error_reply("match locked|"..matchId.."|"..existLock)
end

local matchData = redis.call("hget",matchDataKey,matchId)
if matchData  and lockFlag == "True"  then

    redis.call("set",matchLockIdKey,lockId)
    redis.call("set",matchLockTimeKey,"lock")
    redis.call("pexpire",matchLockTimeKey,lockExpireTime)
    redis.call("expire",matchLockIdKey,3600)
end

return matchData


