from pydantic import BaseModel


class SchemasCopy(BaseModel):
    user_input: str
