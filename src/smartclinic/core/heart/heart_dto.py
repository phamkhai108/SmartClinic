# Định nghĩa các Enum cho các trường phân loại
from enum import Enum

from pydantic import BaseModel


class SexEnum(str, Enum):
    M = "M"
    F = "F"

    @property
    def numeric(self):
        mapping = {"M": 0, "F": 1}
        return mapping[self.value]


class ChestPainTypeEnum(str, Enum):
    TA = "TA"
    ATA = "ATA"
    NAP = "NAP"
    ASY = "ASY"

    @property
    def numeric(self):
        mapping = {"TA": 4, "ATA": 3, "NAP": 2, "ASY": 1}
        return mapping[self.value]


class RestingECGEnum(str, Enum):
    Normal = "Normal"
    ST = "ST"
    LVH = "LVH"

    @property
    def numeric(self):
        mapping = {"Normal": 0, "ST": 1, "LVH": 2}
        return mapping[self.value]


class ExerciseAnginaEnum(str, Enum):
    Y = "Y"
    N = "N"

    @property
    def numeric(self):
        mapping = {"Y": 1, "N": 0}
        return mapping[self.value]


class STSlopeEnum(str, Enum):
    Up = "Up"
    Flat = "Flat"
    Down = "Down"

    @property
    def numeric(self):
        mapping = {"Up": 1, "Flat": 2, "Down": 3}
        return mapping[self.value]


class PredictHeartRequestDto(BaseModel):
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


class PredictResponseDto(BaseModel):
    prediction: int
    message: str
