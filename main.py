import os
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel,RunConfig,Agent,Runner,function_tool,RunContextWrapper,GuardrailFunctionOutput, input_guardrail,InputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent
import requests
import json
import chainlit as cl
import sqlite3
from pydantic import BaseModel
from typing import List


load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")

external_client=AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)
run_config=RunConfig(
    model=model,
    tracing_disabled=True
)

@function_tool
def get_products_info() -> str:
    """
    Fetch product information from the external API.

    This function sends a GET request to the products API endpoint and 
    retrieves product data in JSON format. If the request is successful 
    (status code 200), the JSON response is converted to a string and returned. 
    Otherwise, it returns an error message with the status code.

    Returns:
        str: A JSON-formatted string containing product data on success,
             or an error message if the request fails.
    """
    url = "https://template-03-api.vercel.app/api/products"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return json.dumps(data)  
    else:
        return f"Error: {response.status_code}"


@function_tool
def get_return_policy() -> str:
    """
    Reads the store's return policy from returnpolicy.txt and returns it as a formatted string.
    
    Returns:
        str: Full return policy content, or an error message if the file is missing/empty.
    """
    try:
        with open("returnpolicy.txt", "r", encoding="utf-8") as file:
            policy_content = file.read().strip()
        
        if not policy_content:
            return "Return policy file is empty. Please update newfile.txt with valid content."
        
        return " STORE RETURN POLICY \n\n" + policy_content
    
    except FileNotFoundError:
        return "ERROR: returnpolicy.txt file not found. Please make sure the file exists in the working directory."
    except Exception as e:
        return f"ERROR reading returnpolicy.txt: {str(e)}"
    


@function_tool
def get_faqs() -> str:
    """
    Reads the store FAQs from faqs.txt and returns them as a formatted string.
    The Inquiry Agent can use this to answer customer questions.
    
    Returns:
        str: Complete FAQ content with clear Q&A pairs, or error message if file not found.
    """
    try:
        with open("faqs.txt", "r", encoding='utf-8') as f:
            faq_content = f.read().strip()
            
        if not faq_content:
            return "FAQs file is empty. Please add FAQ content to faqs.txt."
            
        formatted_faqs = " STORE FAQs\n\n" + faq_content
        
        faq_count = faq_content.count('Q:')
        formatted_faqs += f"\n\n Total FAQs loaded: {faq_count} "
        
        return formatted_faqs
        
    except FileNotFoundError:
        return "ERROR: faqs.txt file not found. Please ensure faqs.txt exists in the working directory."
    except Exception as e:
        return f"ERROR reading faqs.txt: {str(e)}"
    



@function_tool
def get_order_status(customer_name: str = None, order_id: int = None) -> str:
    """
    Fetches the status of an order from the orders.db database.

    Args:
        customer_name (str, optional): Name of the customer
        order_id (int, optional): Order ID

    Returns:
        str: Order status or error message if not found
    """
    

    try:
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()

        if order_id is not None:
            cursor.execute("SELECT order_id, customer_name, product_name, status FROM orders WHERE order_id=?", (order_id,))
        elif customer_name is not None:
            cursor.execute("SELECT order_id, customer_name, product_name, status FROM orders WHERE customer_name=?", (customer_name,))
        else:
            return "Please provide either a customer name or an order ID."

        result = cursor.fetchall()
        conn.close()

        if not result:
            return "No order found matching the provided information."

        response = []
        for order in result:
            response.append(f"Order ID: {order[0]}, Customer: {order[1]}, Product: {order[2]}, Status: {order[3]}")

        return "\n".join(response)

    except Exception as e:
        return f"Error fetching order: {str(e)}"


Escalation_Agent = Agent(
    name="Escalation Agent",
    instructions=(
        "You are the Escalation Agent for a Nike store. "
        "Your role is to handle queries that other agents cannot fully resolve due to complexity, ambiguity, or emotional sensitivity. "
        "You do NOT attempt to solve the issue yourself. Instead, do the following:\n"
        "1. Draft a polite, professional acknowledgment of the customer's concern.\n"
        "2. Reassure the customer that their case has been escalated to a human representative.\n"
        "3. Summarize the issue for the support team with key details: customer's request, context, and urgency if apparent.\n"
        "4. Maintain a professional, empathetic, and helpful tone.\n"
    ),
    handoff_description="Handles queries requiring human review, empathy, or multi-layered resolution."
)


product_agent = Agent(
    name="Products Agent",
    instructions=(
        "You are the Products Agent for Nike store products. Always use the `get_products_info` tool before answering. "
        "The tool provides: productName, category, price (PKR), inventory, colors, status, image, and description.\n"
        "Guidelines:\n"
        "- Always provide exact price, stock as numbers.\n"
        "- If size or other info is missing, respond: 'Sorry, size information is not available.'\n"
        "- For images, return only the `image` URL.\n"
        "- For comparisons, filter and compare price, category, inventory, colors, status, and description.\n"
        "- Handle filtering, sorting, and vague queries by matching keywords and context.\n"
        "- If unrelated to Nike products, politely clarify you only provide Nike product info in PKR.\n"
        "- Do not guess or fabricate information; only use tool data.\n"
        "- Support queries in English or mixed languages (e.g., English + Urdu).," \
        "If user ask to describe describe the product"
    ),
    handoff_description="Handles questions about products, availability, price, and details.",
    handoffs=[Escalation_Agent],
    tools=[get_products_info]
)

OrderTracking_Agent = Agent(
    name="Order Tracking Agent",
    instructions=(
        "You are the Order Tracking Agent for a Nike store. "
        "Your role is to provide customers with the status of their orders. "
        "You can use the `get_order_status` tool to retrieve order status using either the customer's name or the order ID. "
        "If the order is not found, inform the user politely and suggest checking the details again."
    ),
    tools=[get_order_status],
    handoffs=[Escalation_Agent],
    handoff_description="Handles queries related to order tracking and status."
)


Returns_Agent = Agent(
    name="Returns Agent",
    instructions=(
        "You are the Returns Agent for a Nike shoes store. "
        "Always call the `get_return_policy` tool to retrieve the latest return/cancellation/refund/exchange rules. "
        "Use the policy to guide the customer step by step through the process. "
        "Do not just dump the policy; interpret it and apply it to the customer's situation. "
        "If the user query is outside your scope, escalate to the Escalation Agent."
        "Never ask for order Number Just tell according to policy."
        "You cant return actual order always ask to contact (support@nikestore.com) or phone (+92-XXX-XXXXXXX)."
        "- If the request is outside your scope (e.g., tracking delivery), delegate to the appropriate agent."
    ),
    tools=[get_return_policy],
    handoffs=[Escalation_Agent,OrderTracking_Agent],
    handoff_description="Handles queries about returns, cancellations, refunds, exchanges, replacements, warranty claims, or defective items."
)


Inquiry_Agent = Agent(
    name="Inquiry Agent",
    instructions=(
        "You are the Inquiry Agent for a Nike shoes store. "
        
        "PROCESS:"
        "1. ALWAYS call `get_faqs` tool to get FAQ data"
        "2. Search the FAQ text for relevant Q&A pairs"
        "3. Provide the answer from the matching FAQ"
        
        "The FAQ database contains these topics (among others):"
        "- Store hours (Q: What are your store hours?)"
        "- Store location (Q: Where are you located?)"
        "- Home delivery (Q: Do you offer home delivery?)"
        "- Delivery fees (Q: What is the delivery fee?)"
        "- Payment methods (Q: What payment methods do you accept?)"
        "- Contact information (Q: How can I contact customer support?)"
        
        "Do not claim information is missing if it exists in the FAQs. "
        "Only escalate if there's genuinely no matching FAQ topic."
    ),
    tools=[get_faqs],
    handoffs=[Escalation_Agent,Returns_Agent,OrderTracking_Agent],
    handoff_description="Handles general inquiries about the store, delivery, shipping, payment methods, promotions, hours, or non-Nike brands."
)


class NikeGuardrailOutput(BaseModel):
    is_inappropriate: bool
    reasoning: str

guardrail_agent = Agent(
    name="Nike Store Guardrail",
    instructions="Check if the user is asking something inappropriate for a Nike store chatbot. Only block clearly harmful, offensive, or completely unrelated requests.",
    output_type=NikeGuardrailOutput,
)

@input_guardrail
async def nike_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context, run_config=run_config)
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate,
    )


Orchestrator_Agent = Agent(
    name="Orchestrator Agent",
    instructions=(
        "You are the Orchestrator Agent for a Nike store. "
        "Your role is to analyze the customer query and delegate it to the appropriate specialized agent.\n"
        "Guidelines:\n"
        "When you delegate, you must immediately execute that agent and return its final response directly to the customer. "
        "Do NOT only say 'transferring you'. The customer should always receive the full answer from the delegated agent."
        "- Products Agent: For Nike product queries (availability, price, stock, category, colors, images, descriptions, sorting, comparisons).\n"
        "- Inquiry Agent: For general store questions (hours, location, delivery, fees, payment methods, promotions, contact info).\n"
        "- Returns Agent: For returns, cancellations, refunds, exchanges, replacements, or warranty issues.\n"
        "- Order Tracking Agent: For checking order status using order ID or customer name.\n"
        "- Escalation Agent: For complex, sensitive, or multi-layered queries.\n"
        "- If multiple intents exist, prioritize routing by main intent.\n"
        "- Always maintain polite, professional, and empathetic tone." \
        "If queries dont make sense dont delegate just respond accordingly."
    ),
    handoffs=[product_agent, Inquiry_Agent, Returns_Agent, OrderTracking_Agent, Escalation_Agent], 
    input_guardrails=[nike_guardrail]
)



MAX_HISTORY = 20

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hello, welcome to the Nike Store Chat Assistant!").send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history") or []
    msg = cl.Message(content="")
    await msg.send()

    history.append({"role": "user", "content": message.content})

    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]

    try:
        result = Runner.run_streamed(
            starting_agent=Orchestrator_Agent,
            input=history,
            run_config=run_config
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                await msg.stream_token(event.data.delta)

        history.append({"role": "assistant", "content": result.final_output})

    except InputGuardrailTripwireTriggered:
        msg.content = "⚠️ Your message contains unsafe content and was blocked."
        await msg.update()

    cl.user_session.set("history", history)