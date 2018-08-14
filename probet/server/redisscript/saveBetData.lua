local playerDataKey = KEYS[1]
local playerLockIdKey = KEYS[2]
local playerLockTimeKey = KEYS[3]
local guessHistorySortKey = KEYS[4]
local guessHistoryHashKey = KEYS[5]

local guessHistoryHashKey_new = KEYS[6]
local guessMemberTeamDataKey = KEYS[7]
local guessDataKey = KEYS[8]
local guessDataDirty = KEYS[9]
local guessLockIdKey = KEYS[10]
local guessLockTimeKey = KEYS[11]


if not guessMemberTeamDataKey then
    return redis.error_reply("invalid guessMemberTeamDataKey")
end


if not guessDataKey then
    return redis.error_reply("invalid guessDataKey")
end


local guessBytes = ARGV[1]
local guessId = ARGV[2]
local guessLock = ARGV[3]
local guessHistoryUId = ARGV[4]
local addTime = ARGV[5]
local playerBytes = ARGV[6]
local playerId = ARGV[7]
local playerLock = ARGV[8]
local guessHistoryUId = ARGV[9]
local guessHistoryTime = ARGV[10]
local guessHistoryBytes = ARGV[11]



local guessExistLock = redis.call("get",guessLockIdKey)

if guessExistLock and guessLock ~= guessExistLock then
    return redis.error_reply("guess lock id not same")
end

redis.call("select",1)
local playerExistLock = redis.call("get",playerLockIdKey)

if playerExistLock and playerLock ~= playerExistLock then
    return redis.error_reply("player lock id not same")
end


redis.call("hset",playerDataKey,playerId,playerBytes)
redis.call("del",playerLockIdKey)
redis.call("del",playerLockTimeKey)

redis.call("zadd",guessHistorySortKey,guessHistoryTime,guessHistoryUId)
redis.call("hset",guessHistoryHashKey,guessHistoryUId,guessHistoryBytes)
redis.call("sadd",guessHistoryHashKey_new,guessHistoryUId)


redis.call("select",2)
redis.call("zadd",guessMemberTeamDataKey,addTime,guessHistoryUId)
redis.call("hset",guessDataKey,guessId,guessBytes)
redis.call("del",guessLockIdKey)
redis.call("del",guessLockTimeKey)
redis.call("sadd",guessDataDirty,guessId)
