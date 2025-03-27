# Định nghĩa các Enum cho các trường phân loại
from enum import IntEnum

from pydantic import BaseModel


class SexEnum(IntEnum):
    M = 0
    F = 1

class ChestPainTypeEnum(IntEnum):
    TA = 4
    ATA = 3
    NAP = 2
    ASY = 1

class RestingECGEnum(IntEnum):
    Normal = 0
    ST = 1
    LVH = 2

class ExerciseAnginaEnum(IntEnum):
    Y = 1
    N = 0

class STSlopeEnum(IntEnum):
    Up = 1
    Flat = 2
    Down = 3

# Sửa lại PredictData sử dụng Enum để Swagger hiển thị dropdown
class PredictData(BaseModel):
    Age: int
    Sex: SexEnum
    ChestPainType: ChestPainTypeEnum
    RestingBP: int
    Cholesterol: int
    FastingBS: int
    RestingECG: RestingECGEnum
    MaxHR: int
    ExerciseAngina: ExerciseAnginaEnum
    Oldpeak: float
    ST_Slope: STSlopeEnum