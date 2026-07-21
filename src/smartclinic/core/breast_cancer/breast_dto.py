from pydantic import BaseModel, Field


class PredictBreastRequest(BaseModel):
    radius_mean: float
    texture_mean: float
    perimeter_mean: float
    area_mean: float
    smoothness_mean: float
    compactness_mean: float
    concavity_mean: float
    concave_points_mean: float = Field(alias="concave points_mean")
    radius_se: float
    perimeter_se: float
    area_se: float
    concavity_se: float
    radius_worst: float
    texture_worst: float
    perimeter_worst: float
    area_worst: float
    smoothness_worst: float
    compactness_worst: float
    concavity_worst: float
    concave_points_worst: float = Field(alias="concave points_worst")
    symmetry_worst: float

    model_config = {"populate_by_name": True}


class PredictBreastResponse(BaseModel):
    prediction: int
    message: str
