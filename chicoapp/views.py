from decouple import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        data = request.POST
        parsed_data = {key: data[key] for key in data}

        print(f"Received: {parsed_data}")

        account_sid = config('ACCOUNT_SID')
        auth_token = config('AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        # Forward the message to GPT using LangChain
        openai_api_key = config('OPENAI_API_KEY')
        tools = []
        llm = ChatOpenAI(api_key=openai_api_key)

        def chatbot(state: State):
            return {"messages": [llm.invoke(state["messages"])]}
        llm_with_tools = llm.bind_tools(tools)

        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.set_entry_point("chatbot")
        graph_builder.set_finish_point("chatbot")
        graph = graph_builder.compile()

        for event in graph.stream({"messages": [{"role": "user", "content": parsed_data["Body"]}]}):
            for value in event.values():
                gpt_response = value["messages"][-1].content
                client.messages.create(
                    from_='whatsapp:+14155238886',
                    body=f"{gpt_response}",
                    to=parsed_data["From"]
                )
                return JsonResponse({"message": "Received", "data": parsed_data, "gpt_response": gpt_response}, status=200)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)
