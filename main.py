import json
import os
import urllib.parse
import urllib.request

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
CLASSIFIER_MODEL = "gpt-4o-mini"
NUTRITION_MODEL = "gpt-4o-mini"

_openai_client: OpenAI | None = None


def openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


class Nutrition(BaseModel):
    kcal: float
    protein: float
    carbs: float


class IsBrandedDecision(BaseModel):
    branded: bool


class FoodDetails(BaseModel):
    description: str
    qa: list[tuple[str, str]]


class DetailsAssessment(BaseModel):
    sufficient: bool
    questions: list[str]


def assess_details(description: str) -> DetailsAssessment:
    response = openai_client().responses.parse(
        model=CLASSIFIER_MODEL,
        input=(
            "A user wants to log the calories, protein, and carbs for something they ate. "
            "Decide whether their description gives enough information to make a realistic "
            "estimate for the portion they actually consumed. Consider quantity/portion size, "
            "preparation method, and key ingredients. "
            "If it is NOT enough, write up to 3 specific clarifying questions (not yes/no). "
            "If it IS enough, set sufficient=true and return no questions. "
            f"Description: {description!r}"
        ),
        text_format=DetailsAssessment,
    )
    return response.output_parsed


def ask_food_details() -> FoodDetails:
    description = input("What did you eat? ").strip()
    assessment = assess_details(description)

    qa: list[tuple[str, str]] = []
    if not assessment.sufficient:
        for question in assessment.questions[:3]:
            answer = input(f"{question} ").strip()
            qa.append((question, answer))

    return FoodDetails(description=description, qa=qa)



def is_branded(query: str) -> bool:
    response = openai_client().responses.parse(
        model=CLASSIFIER_MODEL,
        input=(
            "Decide if the food query refers to a specific commercial/branded product "
            "(e.g., 'Pure Protein Bar', 'Oreo cookies', 'Trader Joe's Mandarin Orange Chicken') "
            "versus a generic food (e.g., 'rice', 'cheddar cheese', 'homemade roti'). "
            f"Query: {query!r}"
        ),
        text_format=IsBrandedDecision,
    )
    return response.output_parsed.branded


def usda_search(query: str, page_size: int = 10) -> dict:
    params = {
        "api_key": os.environ["USDA_API_KEY"],
        "query": query,
        "pageSize": page_size,
    }
    url = f"{USDA_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def _extract_nutrition(food: dict) -> Nutrition | None:
    targets = {
        "Energy": "kcal",
        "Protein": "protein",
        "Carbohydrate, by difference": "carbs",
    }
    values: dict[str, float] = {}
    for n in food.get("foodNutrients", []):
        name = n.get("nutrientName")
        if name in targets and "value" in n:
            values[targets[name]] = float(n["value"])
    if {"kcal", "protein", "carbs"} <= values.keys():
        return Nutrition(**values)
    return None


def estimate_with_llm(details: FoodDetails) -> Nutrition:
    context = [f"Food: {details.description!r}"]
    for question, answer in details.qa:
        context.append(f"Q: {question}\nA: {answer}")

    response = openai_client().responses.parse(
        model=NUTRITION_MODEL,
        input=(
            "Estimate the nutrition for the food the user actually ate, using the description "
            "and any follow-up answers below. Return: kcal (calories), protein (grams), "
            "carbs (grams). Use realistic values for the portion described.\n\n"
            + "\n".join(context)
        ),
        text_format=Nutrition,
    )
    return response.output_parsed


def search_food(details: FoodDetails) -> dict:
    nutrition = estimate_with_llm(details)
    return {**nutrition.model_dump(), "source": "llm", "match": details.description}


def main():
    details = ask_food_details()
    result = search_food(details)
    print(result)


if __name__ == "__main__":
    main()
