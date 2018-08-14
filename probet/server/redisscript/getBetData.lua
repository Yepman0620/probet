local matchDataKey = KEYS[1]
local matchLockIdKey = KEYS[2]
local matchLockTimeKey = KEYS[3]

local guessDataKey = KEYS[4]
local guessLockIdKey = KEYS[5]
local guessLockTimeKey = KEYS[6]

local playerDataKey = KEYS[7]
local playerLockIdKey = KEYS[8]
local playerLockTimeKey = KEYS[9]



local matchId = ARGV[1]
local guessId = ARGV[2]
local guessLock = ARGV[3]
local lockExpireTime = ARGV[4]
local accountId = ARGV[5]
local accountLock = ARGV[6]


local matchData = redis.call("hget",matchDataKey,matchId)

local existGuessLock = redis.call("get",guessLockIdKey)
local existGuessLockTime = redis.call("get",guessLockTimeKey)

if existGuessLock and existGuessLockTime then
    return redis.error_reply("match locked|"..guessId.."|"..existGuessLock)
end

local guessData = redis.call("hget",guessDataKey,guessId)
if guessData then

    redis.call("set",guessLockIdKey,guessLock)
    redis.call("set",guessLockTimeKey,"lock")
    redis.call("pexpire",guessLockTimeKey,lockExpireTime)
    redis.call("expire",guessLockIdKey,3600)
end


redis.call("select",1)
local existPlayerLock = redis.call("get",playerLockIdKey)
local existPlayerLockTime = redis.call("get",playerLockTimeKey)

if existPlayerLock and existPlayerLockTime then
    return redis.error_reply("player locked|"..accountId.."|"..existPlayerLock)
end

local playerData = redis.call("hget",playerDataKey,accountId)
if playerData then
    redis.call("set",playerLockIdKey,accountLock)
    redis.call("set",playerLockTimeKey,"lock")
    redis.call("pexpire",playerLockTimeKey,lockExpireTime)
    redis.call("expire",playerLockIdKey,3600)
end


local retTable = {}
retTable[1] = matchData
retTable[2] = guessData
retTable[3] = playerData

return retTable

