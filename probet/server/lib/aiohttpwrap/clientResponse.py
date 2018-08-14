
from aiohttp.client_reqrep import ClientResponse

from aiohttp.streams import FlowControlStreamReader



class aiohttpFlowControlStreamReader(FlowControlStreamReader):
    def __init__(self,protocol, buffer_limit=2**32,*args, **kwargs):
        super(aiohttpFlowControlStreamReader, self).__init__(*args, **kwargs)

class aiohttpClientResponseWrap(ClientResponse):
    def __init__(self,*args, **kwargs):

        flow_control_class = aiohttpFlowControlStreamReader

        super(aiohttpClientResponseWrap, self).__init__(*args, **kwargs)
