from pydantic import BaseModel


class SchemasCopy(BaseModel):
    user_input: str
    previous_user_message: str | None = None
    previous_bot_reply: str | None = None


class AnalyseBody(BaseModel):
    schema: str