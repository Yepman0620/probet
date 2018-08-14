

local DataKey = KEYS[1]
local LockIdKey = KEYS[2]
local LockTimeKey = KEYS[3]


local uniqueId = ARGV[1]
local lockFlag = ARGV[2]
local lockId = ARGV[3]
local lockExpireTime = ARGV[4]


if not DataKey then
    return redis.error_reply("invalid DataKey")
end


if not LockIdKey then
    return redis.error_reply("invalid LockIdKey")
end

if not LockTimeKey then
    return redis.error_reply("LockTimeKey")
end


local existLock = redis.call("get",LockIdKey)
local existLockTime = redis.call("get",LockTimeKey)

if lockFlag == "True" and existLock and existLockTime then
    return redis.error_reply("player locked|"..uniqueId.."|"..existLock)
end

local playerData = redis.call("hget",DataKey,uniqueId)
if playerData and lockFlag == "True"  then

    redis.call("set",LockIdKey,lockId)
    redis.call("set",LockTimeKey,"lock")
    redis.call("pexpire",LockTimeKey,lockExpireTime)
    redis.call("expire",LockIdKey,3600)

end

return playerData


