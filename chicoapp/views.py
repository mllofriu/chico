from decouple import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client


@csrf_exempt
def webhook(request):
    if request.method == "POST":
        data = request.POST
        parsed_data = {key: data[key] for key in data}

        print(f"Received: {parsed_data}")

        account_sid = config('ACCOUNT_SID')
        auth_token = config('AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=f"I heard: {parsed_data["Body"]}",
            to=parsed_data["From"]
        )

        return JsonResponse({"message": "Received", "data": parsed_data}, status=200)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)
