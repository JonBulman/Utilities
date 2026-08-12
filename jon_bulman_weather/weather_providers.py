import requests
import json
import arrow
import jon_bulman_weather

def GetForecastsolarWeatherData(url, for_date, debug_level):

    solar_estimate = -1.0
    print(url)
    response_API = requests.get(url)#, auth=(api_key,''))
    if response_API.status_code != 200:
        if debug_level > 0:
            print("...GetWeatherData",response_API.status_code)
        else:
            print("Failed to get ",response_API.status_code)
            return solar_estimate
    data = json.loads(response_API.text)

# Loop over forecast to produce body to print
    w_data = data["result"]
    #print(w_data)
    try:
        solar_estimate = w_data[for_date]
    except Exception as e:
        print("No data for date ",for_date,e)

    return solar_estimate

def GetSolcastWeatherData(url, api_key, for_date, debug_level):
    print(url)
    weather_data = []
    response_API = requests.get(url, auth = (api_key,''))
    if response_API.status_code != 200:
        if debug_level > 0:
            print("...GetWeatherData",response_API.status_code)
        else :
            print("Failed to get ",response_API.status_code, api_key)
            return weather_data

    data = json.loads(response_API.text)

    
# Loop over forecast to produce body to print
    w_data = data["forecasts"]

# break down each product
    for ct, product in enumerate(w_data):
        pe = product["pv_estimate"]
        # only bother if there is some PV (for now)
        pe10 = product["pv_estimate10"]
        pe90 = product["pv_estimate90"]
        pend = product["period_end"]
        period = product["period"]

        splitdata = pend.split("T")
        date = splitdata[0]
        if date == for_date : # only add if matching date
            ad = jon_bulman_weather.Solcast_Breakdown(pe, pe10, pe90, pend, period)
            weather_data.append(ad)
            if debug_level > 0:
                ad.Solcast_Print()
    return weather_data

def GetVisualCrossingWeatherData(url, for_date, debug_level):

    solar_estimate = -1.0
    print(url)
    response_API = requests.get(url)
    if response_API.status_code != 200:
        if debug_level > 0:
            print("...GetWeatherData",response_API.status_code)
        else:
            print("Failed to get ",response_API.status_code)
            return solar_estimate
    data = json.loads(response_API.text)

# Loop over forecast to produce body to print
    w_data = data["days"]
    # print(w_data)
    try:
        # date=w_data[0]
        for ct, product in enumerate(w_data):
            dt = product["datetime"]
            if dt == for_date:
                solar_estimate = product["solarenergy"]
                break
        # print(date)
    except Exception as e:
        print("No data for date ",for_date,e)

    return solar_estimate

def get_stormglassio(api_key) :
    # https://docs.stormglass.io/#/tide?id=sea-levels-and-datums

    start = arrow.now().floor('day')
    end = arrow.now().shift(days=1).floor('day')

    response = requests.get('https://api.stormglass.io/v2/tide/sea-level/point',
        params={
            'lat': 50.162259246444606,
            'lng': -5.059666804253347543,
            'end': end.to('UTC').timestamp(),  # Convert to UTC timestam
            'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        },
        headers={
            'Authorization': '2478a270-95c7-11f1-b11b-0242ac120004-2478a2ca-95c7-11f1-b11b-0242ac120004'
        }
    )
    #response = requests.get('https://api.stormglass.io/v2/tide/stations/area',
    #    headers={
    #        'Authorization': '2478a270-95c7-11f1-b11b-0242ac120004-2478a2ca-95c7-11f1-b11b-0242ac120004'
    #    },
    #    params={
    #    }
    #        'box': '51.0,-4:49,-6'
    #'https://api.stormglass.io/v2/tide/stations',
    #)

        # Do something with response data.
    json_data = response.json()
    with open("tidedata.json", "w") as f_out:
        json.dump(json_data, f_out, indent=3)


