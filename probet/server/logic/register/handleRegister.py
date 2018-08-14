from csprotocol.protocol import *


g_obj_handlerRegister = {}

from logic.clienthandler import msgGetMatchList
g_obj_handlerRegister[getMatchList] = msgGetMatchList.handleGetMatchList

from logic.clienthandler import msgGuessBet
g_obj_handlerRegister[guessBet] = msgGuessBet.handleGuessBet


from logic.clienthandler import msgGetOneMatch
g_obj_handlerRegister[getOneMatch] = msgGetOneMatch.handleGetOneMatch

from logic.clienthandler import msgGetGuessBetList
g_obj_handlerRegister[getGuessBetList] = msgGetGuessBetList.handleGetGuessBetList

from logic.clienthandler import msgGetGuessResultList
g_obj_handlerRegister[getGuessResultList] = msgGetGuessResultList.handleGetGuessResultList