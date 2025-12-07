from google.adk.agents import Agent
from google.genai import types
import requests

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"


def get_user_agent(customer_id: str, model_name: str = "gemini-2.5-flash-lite"):
    """
    Creates an Agent instance bound to a specific customer_id.
    The tools defined here capture customer_id from the closure.
    """

    # --- Tool Definitions (Scoped to customer_id) ---

    def get_my_account_status() -> dict:
        """Retrieves the verification status of your account."""
        try:
            response = requests.get(
                f"{API_BASE_URL}/account/status/{customer_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def check_my_card_delivery() -> dict:
        """Checks the delivery status and tracking ETA of your physical card."""
        try:
            response = requests.get(
                f"{API_BASE_URL}/card/status/{customer_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_my_bill() -> dict:
        """Fetches your current billing details including total due and due date."""
        try:
            response = requests.get(f"{API_BASE_URL}/bill/{customer_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def make_payment(amount: float, method: str) -> dict:
        """
        Initiates a payment for your account.
        Args:
            amount: Amount to pay.
            method: 'UPI', 'Card', or 'Netbanking'.
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/payment/initiate/{customer_id}",
                json={"amount": amount, "method": method}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_recent_transactions(limit: int = 5) -> dict:
        """
        Fetches your recent transactions.
        Args:
            limit: Number of transactions (default 5).
        """
        try:
            response = requests.get(
                f"{API_BASE_URL}/transactions/{customer_id}", params={"limit": limit})
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def convert_to_emi(txn_id: str, tenure_months: int) -> dict:
        """
        Converts a specific transaction into EMI installments.
        Args:
            txn_id: The ID of the transaction (found in recent transactions).
            tenure_months: Duration in months (3-24).
        """
        try:
            # Note: This tool still needs txn_id, but doesn't need customer_id
            response = requests.post(
                f"{API_BASE_URL}/emi/convert",
                json={"txn_id": txn_id, "tenure_months": tenure_months}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # --- System Instruction ---
    # Simplified instructions because identification is now handled by the system
    system_prompt = """
    You are the 'OneCard GenAI Assistant'. You help the currently logged-in customer manage their credit card.
    
    CORE RULES:
    1. **Context:** You are already authenticated. Do not ask for Name, Phone, or Customer ID.
    2. **Safety:** Before processing a payment or EMI conversion, explicitly confirm the details (amount/tenure) with the user.
    3. **Data Handling:** When you get data (like a bill or transaction list), summarize it clearly.
    4. **Tone:** Be professional, empathetic, and concise.
    """

    # --- Agent Creation ---
    agent = Agent(
        name="OneCardBot",
        model=model_name,
        instruction=system_prompt,
        tools=[
            get_my_account_status,
            check_my_card_delivery,
            get_my_bill,
            make_payment,
            get_recent_transactions,
            convert_to_emi
        ],
        output_key="final_response",
    )

    return agent
