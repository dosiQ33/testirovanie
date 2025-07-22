from enum import Enum

class RegionEnum(Enum):
    rk = "RK"
    oblast = "OBLAST"
    raion = "RAION"
    building = "BUILDING"

class FloorEnum(Enum):
    np = "NP"
    esf = "ESF"
    fno = "FNO"
    kkm = "KKM"