
local playerDataKey = KEYS[1]
local playerDataDirtyKey = KEYS[2]
local playerDataNewDirtyKey = KEYS[3]
local playerLockIdKey = KEYS[4]
local playerLockTimeKey = KEYS[5]



local accountId = ARGV[1]
local playerBytes = ARGV[2]
local lockId = ARGV[3]
local setDirty = ARGV[4]
local setNew = ARGV[5]


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

if existLock and lockId ~= existLock then
    return redis.error_reply("lock id not same")
end

redis.call("hset",playerDataKey,accountId,playerBytes)
redis.call("del",playerLockIdKey)
redis.call("del",playerLockTimeKey)

if setDirty == "True" then
    redis.call("sadd", playerDataDirtyKey,accountId)
end


if setNew == "True" then
    redis.call("sadd", playerDataNewDirtyKey,accountId)
end
