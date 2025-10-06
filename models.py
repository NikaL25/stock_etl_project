from pydantic import BaseModel, Field, validator
from typing import Dict

class DailyStockData(BaseModel):
    open: float = Field(..., alias="1. open")
    high: float = Field(..., alias="2. high")
    low: float = Field(..., alias="3. low")
    close: float = Field(..., alias="4. close")
    volume: int = Field(..., alias="5. volume")

    @validator("*", pre=True)
    def convert_to_float_or_int(cls, v):
        return float(v) if '.' in v else int(v)

class AlphaVantageResponse(BaseModel):
    TimeSeries: Dict[str, DailyStockData] = Field(..., alias="Time Series (Daily)")
