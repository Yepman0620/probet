import asyncio
from sqlalchemy.ext.compiler import compiles
from lib.jsonhelp import classJsonDump
from sqlalchemy.sql.expression import Executable, ClauseElement
from sqlalchemy.sql import select,insert

class InsertFromSelect(Executable, ClauseElement):
    def __init__(self, table,select):
        self.table = table
        self.select = select

@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    return "REPLACE INTO %s VALUES (%s)" % (
        compiler.process(element.table, asfrom=True),
        compiler.process(element.select)
    )


class cResp():
    def __init__(self):
        self.ret = 0
        self.retDes = ""
        self.data = []

@asyncio.coroutine
def handleHttp(request):
    from gmweb.utils.models import tb_pinbo_wagers
    # tb_pinbo_wagers.replace()
    tb_pinbo_wagers.update().values()
    # replace into tbl_name set col_name = value
    # insert = InsertFromSelect(tb_pinbo_wagers,)
    resp=cResp()
    return classJsonDump.dumps(resp)