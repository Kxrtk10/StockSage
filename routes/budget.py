import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
router = APIRouter(tags=["budget"])


class BudgetRequest(BaseModel):
    amount: float
    currency: str
    risk: str
    horizon: str


@router.post("/api/budget")
async def budget(request: BudgetRequest):
    try:
        currency_symbol = "₹" if request.currency == "INR" else "$"
        market_name = "Indian Market (NSE/BSE)" if request.currency == "INR" else "US Market (NASDAQ/NYSE)"

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system="You are a portfolio advisor for StockSage AI. Return ONLY valid JSON with absolutely no markdown, no backticks, no explanation text outside the JSON. The JSON must have this exact structure: {summary: string, riskLevel: string, allocations: array}. riskLevel must be exactly Low, Moderate, or High. Each allocation in the array must have: name (string), percentage (integer), amount (integer), color (hex string), rationale (string), examples (array of 3 stock name strings). Use 4 to 5 allocations that sum to exactly 100. Calculate amount as round of percentage divided by 100 multiplied by the budget amount. For colors use these in order: #6c63ff, #22c55e, #f59e0b, #ef4444, #06b6d4. The summary should be 2 to 3 sentences in plain English explaining the strategy and encouraging the user. Always tailor recommendations to the specified market — Indian stocks for INR, US stocks for USD. Never return anything outside the JSON object.",
            messages=[
                {
                    "role": "user",
                    "content": f"Budget: {currency_symbol}{request.amount}, Market: {market_name}, Risk: {request.risk}, Horizon: {request.horizon}. Build me a smart portfolio allocation.",
                }
            ],
        )

        response_text = message.content[0].text.strip()
        response_text = response_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(response_text)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail="Something went wrong while creating your budget plan.")
