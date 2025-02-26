from decouple import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

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
        llm = OpenAI(api_key=openai_api_key)
        prompt = PromptTemplate(input_variables=["message"], template="Respond to the following message: {message}")
        chain = LLMChain(llm=llm, prompt=prompt)
        gpt_response = chain.run(message=parsed_data["Body"])

        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=f"GPT-3 says: {gpt_response}",
            to=parsed_data["From"]
        )

        return JsonResponse({"message": "Received", "data": parsed_data, "gpt_response": gpt_response}, status=200)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)
