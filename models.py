from pydantic import BaseModel

class Nutrition(BaseModel):
    kcal: float
    protein: float
    carbs: float


class IsBrandedDecision(BaseModel):
    branded: bool


class FoodDetails(BaseModel):
    description: str
    qa: list[tuple[str, str]]
    
class FoodDetailsBasic(BaseModel):
    description: str


class GeneratedQuestions(BaseModel):
    questions_txt: str
    
    
    
class DiscordUserInput(BaseModel):
    user_input: str
    
class SupabaseResult(BaseModel):
    result: bool
    
# class DiscordQAUserInput(BaseModel):
#     user_input: str
    
    
class SupabaseGetResult(BaseModel):
    kcal: int 
    protein: int 
    carbs: int 