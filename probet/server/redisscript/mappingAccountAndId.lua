


local mappingAccount2IdKey = KEYS[1]
local mappingId2Account = KEYS[2]

local accountId = ARGV[1]
local shortId = ARGV[2]


redis.call("hset",mappingAccount2IdKey,accountId,shortId)
redis.call("hset",mappingId2Account,shortId,accountId)