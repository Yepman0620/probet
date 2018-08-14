
from enum import Enum


class enumLightRankType(Enum):
    rankTypeAll = "all"         #0 全部排行
    rankTypeWeek = "week"       #1 周排行
    rankTypeMonth = "month"     #2 月排行

enumLightList = [enumLightRankType.rankTypeAll.value,enumLightRankType.rankTypeWeek.value,enumLightRankType.rankTypeMonth.value]