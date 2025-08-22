from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import datetime
from .models import SoilCropRecommendation
from .models import CropDuration
from .models import PlantingCalendar

@csrf_exempt
def dialogflow_webhook(request):
    # print(request)
    # print("****************************")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # print(data)
            intent = data['queryResult']['intent']['displayName']

            if intent == 'get_weather':
                parameters = data['queryResult']['parameters']

                # Handle default city
                city = parameters.get('geo-city')
                if not city or city.strip() == '':
                    city = 'Hyderabad'
                    # print("boo",city,"m")

                # Handle default date
                date = parameters.get('date-time')
                if not date or date.strip() == '':
                    date = datetime.date.today().isoformat()
                    # print("me",date,"rrr")

                # Weather API
                api_key = "b1ecbbe66c7efb6ecacc284013dc655a"
                url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

                try:
                    weather_data = requests.get(url).json()

                    if weather_data.get('cod') != "200":
                        weather_response = f"Sorry, I couldn't find the weather for {city}."
                    else:
                        date=date[:10:]
                        # print(date)
                        #print(weather_data)
                        forecasts = weather_data['list']
                        day_forecasts = [f for f in forecasts if (f['dt_txt'].startswith(date) and (f['dt_txt'].endswith('09:00:00') or f['dt_txt'].endswith('18:00:00')))]
                        parts = [f"Forecast for {city} on {date}:"]
                        # print(day_forecasts)
                        if len(day_forecasts)>=2:
                            parts.append(f"morning 🌅 : {day_forecasts[0]['main']['temp']} C and {day_forecasts[0]['weather'][0]['description']}")
                            parts.append(f"evening 🌇 : {day_forecasts[1]['main']['temp']} C and {day_forecasts[1]['weather'][0]['description']}")
                        elif len(day_forecasts)==1:
                            parts.append(f"morning 🌅 : {day_forecasts[0]['main']['temp']} C and {day_forecasts[0]['weather'][0]['description']}")
                        else:
                            parts.append("sorry iam unable to fetch weather right now")
                        weather_response = "\n".join(parts)

                except Exception as e:
                    weather_response = f"Error fetching weather data: {str(e)}"

                return JsonResponse({"fulfillmentText": weather_response})
            elif intent == 'get_irrigation_advice':
                parameters = data['queryResult']['parameters']
                crop = parameters.get('crop-name')
                soil = parameters.get('soil-type')

                if not crop or not soil:
                    response = "Please provide both the crop type and the soil type."
                else:
                    tip = get_irrigation_tip(crop, soil)
                    if "error" in tip:
                        response = tip["error"]
                    else:
                        response = (
                            f"Irrigation advice for {crop} in {soil} soil:\n\n"
                            f"🌱 Seeding: {tip['seeding']}\n\n"
                            f"🌸 Flowering: {tip['flowering']}\n\n"
                            f"🍓 Fruitful stage: {tip['fruitful']}"
                        )

                return JsonResponse({"fulfillmentText": response})
            elif intent == "crop_recomandition":
                parameters = data['queryResult']['parameters']
                soil = parameters.get('soil-type')
                soil=soil.lower()
                # print("soil is",soil)
                crops = SoilCropRecommendation.objects.filter(soil_type__iexact=soil).order_by('priority')
                # print("*************************")
                # print(crops)
                if crops.exists():
                    crop_list = [crop.crop_name for crop in crops]
                    response_text = f"Crops suitable for {soil} soil in priority order are: " + ", ".join(crop_list)
                else:
                    response_text = f"Sorry, I don't have crop suggestions for {soil} soil yet."

                return JsonResponse({'fulfillmentText': response_text})
            elif intent=='crop_duration':
                parameters=data['queryResult']['parameters']
                crop=parameters.get('crop-name')
                crop=crop.lower()
                # print("crop is ",crop)
                duration=CropDuration.objects.filter(crop_name__iexact=crop)
                if duration.exists():
                    return JsonResponse({"fulfillmentText":str(duration.first())})
                else:
                    return JsonResponse({"fulfillmentText":"As of now I dont have the data of particular crop"})
                print("duration is ",str(duration.first()))
            elif intent=='Planting Calendar':
                # print("&&&&&&&&&&&&&&&&&&&")
                parameters=data['queryResult']['parameters']
                # print(parameters)
                crop=parameters.get('crop-name')
                crop=crop.lower()
                state = parameters.get('geo-state')
                if not state or state.strip() == '':
                    state = 'Telangana'
                # print(crop," ",state)
                try:
                    entry = PlantingCalendar.objects.get(crop_name__iexact=crop, region__iexact=state)
                    print("entry is ",entry)
                    response_text = (
                        f"The best time to plant {entry.crop_name.title()} in {entry.region.title()} "
                        f"is from {entry.planting_start_month} to {entry.planting_end_month}."
                    )
                except PlantingCalendar.DoesNotExist:
                    response_text = (
                        f"Sorry, I couldn't find the planting season for {crop.title()} in {state.title()}."
                    )

                return JsonResponse({
                    "fulfillmentText": response_text
                })
            return JsonResponse({"fulfillmentText": "Sorry, I only handle weather queries for now."})

        except Exception as e:
            return JsonResponse({"fulfillmentText": f"Error: {str(e)}"})

    return JsonResponse({"fulfillmentText": "Only POST requests are accepted."})



from .models import CropSoilIrrigation
def get_irrigation_tip(crop, soil):
    try:
        # print("hii")
        entry = CropSoilIrrigation.objects.get(crop_type__iexact=crop, soil_type__iexact=soil)
        # print(entry)
        return {
            "seeding": entry.seeding_advice,
            "flowering": entry.flowering_advice,
            "fruitful": entry.fruitful_advice
        }
    except CropSoilIrrigation.DoesNotExist:
        # print("hello")
        # print(entry)
        return {
            "error": f"No irrigation data found for crop '{crop}' and soil '{soil}'."
        }
