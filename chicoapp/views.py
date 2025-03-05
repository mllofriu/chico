from decouple import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        data = request.POST
        parsed_data = {key: data[key] for key in data}

        print(f"Received: {parsed_data}")

        return JsonResponse({"message": "Received", "data": parsed_data}, status=200)

    return JsonResponse({"error": "Only POST requests allowed"}, status=405)
