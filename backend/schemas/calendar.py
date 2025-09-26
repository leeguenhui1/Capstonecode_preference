from pydantic import BaseModel


class CalendarEventCreate(BaseModel):
    date: str
    title: str


class CalendarEventResponse(BaseModel):
    id: int
    date: str
    title: str

    class Config:
        from_attributes = True
