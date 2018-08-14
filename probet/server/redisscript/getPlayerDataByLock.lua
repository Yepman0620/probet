

local playerDataKey = KEYS[1]
local playerLockIdKey = KEYS[2]
local playerLockTimeKey = KEYS[3]


local accountId = ARGV[1]
local lockFlag = ARGV[2]
local lockId = ARGV[3]
local lockExpireTime = ARGV[4]


if not playerDataKey then
    return redis.error_reply("invalid playerDataKey")
end


if not playerLockIdKey then
    return redis.error_reply("invalid playerLockIdKey")
end

if not playerLockTimeKey then
    return redis.error_reply("playerLockTimeKey")
end


local existLock = redis.call("get",playerLockIdKey)
local existLockTime = redis.call("get",playerLockTimeKey)

if lockFlag == "True" and existLock and existLockTime then
    return redis.error_reply("player locked|"..accountId.."|"..existLock)
end

local playerData = redis.call("hget",playerDataKey,accountId)
if playerData and lockFlag == "True"  then

    redis.call("set",playerLockIdKey,lockId)
    redis.call("set",playerLockTimeKey,"lock")
    redis.call("pexpire",playerLockTimeKey,lockExpireTime)
    redis.call("expire",playerLockIdKey,3600)

end

return playerData


