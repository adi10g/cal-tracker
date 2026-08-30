import json
import os
import urllib.parse
import urllib.request
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
from datetime import date

from models import Nutrition, IsBrandedDecision, FoodDetails, GeneratedQuestions, DiscordUserInput, FoodDetailsBasic, SupabaseResult, SupabaseGetResult

load_dotenv()
app = FastAPI()
app.generated_questions = ''
app.original_input=''
app.question_response=''
app.summary_text = ''
app.estimate = {}

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

#USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
#CLASSIFIER_MODEL = "gpt-4o-mini"
#CLASSIFIER_MODEL = gpt-5.6-luna
#CLASSIFIER_MODEL = gpt-5.6-terra
#CLASSIFIER_MODEL = "gpt-4o-mini"

NUTRITION_MODEL = "gpt-5.6-luna"
QUESTIONS_MODEL = "gpt-5.6-luna"

_openai_client: OpenAI | None = None


def openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/generate_questions/")
def generate_questions(uinput: DiscordUserInput) -> GeneratedQuestions:
    print(uinput.user_input)
    if len(uinput.user_input) < 1: 
        raise HTTPException(status_code=400, detail="Try again")
    try: 
        response = openai_client().responses.parse(
            model=QUESTIONS_MODEL,
            input=(
                "A user wants to log the calories, protein, and carbs for something they ate. "
                "Decide whether their description gives enough information to make a realistic "
                "estimate for the portion they actually consumed. Consider quantity/portion size, "
                "preparation method, and key ingredients. "
                "Write up to 3 specific clarifying questions, but ask at least one question. "
                "The questions should be written in a free flowing manner, such that the user can respond in one message. The responses to the questions will be without "
                "commas separating each answer, numbers delineating responses, etc. Assume the user will try to respond to the questions without considering "
                "grammar, sentence structure, proper numbering, etc."
                f"Description: {uinput!r}"
            ),
            text_format=GeneratedQuestions,
        )
    except Exception as e: 
            raise HTTPException(status_code=400, detail=f"Backend server error: {e}")
    app.original_input = uinput.user_input
    app.generated_questions = response.output_parsed.questions_txt
    
    #print(response)
    if response.status != "completed":
        raise HTTPException(status_code=400, detail="Backend server error")
    return dict(response.output_parsed)

@app.post("/final_estimate/")
def final_estimate(uinput: DiscordUserInput) -> Nutrition:
    print(uinput.user_input)
    app.question_response=uinput.user_input
    if len(uinput.user_input) < 1: 
        raise HTTPException(status_code=400, detail="Try again")
    #print(type(uinput))
    #if uinput.user_input
    try:
        response = openai_client().responses.parse(
            tools=[{"type": "web_search"}],
            model=NUTRITION_MODEL,
            reasoning={"effort": "low", "summary": "auto"},
            input=(
                "Estimate the nutrition for the food the user actually ate, using the description "
                "and any follow-up answers below. Remember, the food might be branded so if it is use web-search. Return: kcal (calories), protein (grams), "
                "carbs (grams). Use realistic values for the portion described."
                "Included below is the food the user described, along some QnA to understand better.\n\n"
                + app.original_input + "\n\n" + app.generated_questions + "\n\n" + app.question_response
            ),
            text_format=Nutrition,
        )
        #print(response)
        #print(dir(response))
#       print(response.summary)
        #print(response.output)
        #print(dict(response.output))
        #print((dict(response.output))['summary'])
        #print(dict(response.output_parsed)) 
        
    except Exception as e: 
        raise HTTPException(status_code=400, detail=f"Backend server error: {e}")
    
    if response.status != "completed":
        raise HTTPException(status_code=400, detail="Backend server error")
    
    #print(response.output)
    
    app.estimate = dict(response.output_parsed)
    print(response.output)
    
    #app.summary_text = response.output[0].summary[0].text
    
    #print(app.summary_text)
    return app.estimate

@app.post("/log_conversation/")
def log_conversation() -> SupabaseResult:
    response = (
        supabase.table("macros_table_v1")
        .insert(
            {
                "uid": 1,
                "datetime": str(date.today()),
                "original_input": app.original_input , 
                "calories": int(app.estimate['kcal']),
                "protein": int(app.estimate['protein']),
                "carbs": int(app.estimate['carbs']),
                "fats" : 0,
                "questions": app.generated_questions,
                "answers": app.question_response,
                "reasoning": app.summary_text
            }
        ).execute()
    )
    print(app.question_response)
    
    return {"result": True}


@app.get("/get_macros_today/")
def get_macros_today() -> SupabaseGetResult:
    # const { data, error } = await supabase
    # .from('sessions_log')
    # .select()
    # .gt('minutes', 0)
    # .gte('start_time', `${todayDate} 00:00:00`)
    # .lte('start_time', `${todayDate} 23:35:00`) 
    # .eq('status', "Completed"); 
    
    response = (
        supabase.table("macros_table_v1")
        .select("calories, protein, carbs")
        .eq("datetime", f'{str(date.today())} 00:00:00')
        .execute()
    )
    
    sums = {"kcal": 0, "protein": 0, "carbs":0}
    
    for row in response.data: 
        sums['kcal'] += row['calories']
        sums['protein'] += row['protein']
        sums['carbs'] += row['carbs']
        
        
    
    return sums
  
    #        + app.original_input + "\n\n" + app.generated_questions + "\n\n" + uinput.user_input 
    
    #if not response.ok:
    #    raise HTTPException(status_code=400, detail="Backend server error")
    
    
#log_conversation()
    
    




# # Testing just collecting a response
# @app.get("/estimate_noqa")
# def estimate_with_llm(details: FoodDetailsBasic) -> Nutrition:
#     # context = [f"Food: {details.description!r}"]
#     # for question, answer in details.qa:
#     #     context.append(f"Q: {question}\nA: {answer}")

#     response = openai_client().responses.parse(
#         model=NUTRITION_MODEL,
#         input=(
#             "Estimate the nutrition for the food the user actually ate, using the description "
#             "and any follow-up answers below. Return: kcal (calories), protein (grams), "
#             "carbs (grams). Use realistic values for the portion described.\n\n"
#             + "\n".join(details)
#         ),
#         text_format=Nutrition,
#     )
#     return response.output_parsed

# def ask_food_details() -> FoodDetails:
#     description = input("What did you eat? ").strip()
#     assessment = assess_details(description)

#     qa: list[tuple[str, str]] = []
#     if not assessment.sufficient:
#         for question in assessment.questions[:3]:
#             answer = input(f"{question} ").strip()
#             qa.append((question, answer))

#     return FoodDetails(description=description, qa=qa)



# def is_branded(query: str) -> bool:
#     response = openai_client().responses.parse(
#         model=CLASSIFIER_MODEL,
#         input=(
#             "Decide if the food query refers to a specific commercial/branded product "
#             "(e.g., 'Pure Protein Bar', 'Oreo cookies', 'Trader Joe's Mandarin Orange Chicken') "
#             "versus a generic food (e.g., 'rice', 'cheddar cheese', 'homemade roti'). "
#             f"Query: {query!r}"
#         ),
#         text_format=IsBrandedDecision,
#     )
#     return response.output_parsed.branded


# def usda_search(query: str, page_size: int = 10) -> dict:
#     params = {
#         "api_key": os.environ["USDA_API_KEY"],
#         "query": query,
#         "pageSize": page_size,
#     }
#     url = f"{USDA_SEARCH_URL}?{urllib.parse.urlencode(params)}"
#     with urllib.request.urlopen(url) as response:
#         return json.loads(response.read())


# def _extract_nutrition(food: dict) -> Nutrition | None:
#     targets = {
#         "Energy": "kcal",
#         "Protein": "protein",
#         "Carbohydrate, by difference": "carbs",
#     }
#     values: dict[str, float] = {}
#     for n in food.get("foodNutrients", []):
#         name = n.get("nutrientName")
#         if name in targets and "value" in n:
#             values[targets[name]] = float(n["value"])
#     if {"kcal", "protein", "carbs"} <= values.keys():
#         return Nutrition(**values)
#     return None





# def search_food(details: FoodDetails) -> dict:
#     nutrition = estimate_with_llm(details)
#     return {**nutrition.model_dump(), "source": "llm", "match": details.description}

# def log_to_supabase(description, qa): 
    
    
#     return

# # def main():
# #     details = ask_food_details()
# #     log_to_supabase(details.description, details.qa)
# #     response = (
# #         supabase.table("food_log")
# #         .insert({"id": 1, "name": "Pluto"})
# #     .execute()
# # )
# #     result = search_food(details)
# #     print(result)


# if __name__ == "__main__":
#     main()
