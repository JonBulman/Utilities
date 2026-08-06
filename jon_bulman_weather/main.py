#
# Jon Bulman Main Program for Solcast & Forecastsolar Services
#
import argparse
from datetime import datetime, UTC
from datetime import timedelta
import jon_bulman_utilities
import jon_bulman_weather
from jon_bulman_weather.weather_classes import Solar_PV_Data
import json
import sys

# This is your class_map
class_lookup = {
    "Solar_PV_Data": Solar_PV_Data
}

def main():
    # This ensures every time the script starts, it prints a clear timestamp
    todays_date = datetime.now(tz=UTC)
    print(f"\n--- SCRIPTS STARTING: {todays_date} ---\n")

    jon_bulman_utilities.setup_environment()

    # Ask for additional command line arguments if needed (for VSCode)
    parser = argparse.ArgumentParser(description="Get weather information")
    parser.add_argument(
        "--config-file",
        "-c",
        help="Path to the config file (default: settings.json)",
        type=str,
        default="/Users/Jon/input/settings.json")

    # Your other script arguments go here
    # parser.add_argument("--account", help="An Account is required")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", type=int, choices=[0, 1, 2])
    parser.add_argument("--apikey", help="An API_KEY",default=None)
    args = parser.parse_args()

    print(f"Config file: str({args.config_file})")
    config_file = str(args.config_file)

    config = jon_bulman_utilities.Load_Config(config_file)
    if config is None:
        print("No configuration file loaded - exiting")
        sys.exit(1)
    
    # DEBUG level - passed to functions for my debug info
    my_DEBUG_level = 0
    if args.verbose:
        my_DEBUG_level = args.verbose

    output_dir = jon_bulman_utilities.Get_Variable("OUTPUT_DIR",config,my_DEBUG_level)
    if output_dir is None:
        print("No output directory defined - set environment variable OUTPUT_DIR or provide on command line using --output_directory")
        sys.exit(1)

# Free version has to use this....
    solcast_url = jon_bulman_utilities.Get_Variable("SOLCAST_URL",config,my_DEBUG_level)
    if solcast_url is None:
        print("No Solcast URL defined - set environment variable SOLCAST_URL")
        sys.exit(1)
    
    my_Solcast_APIKEY =  jon_bulman_utilities.Get_Variable("SOLCAST_API_KEY",config,my_DEBUG_level)
    if args.apikey:
        # overrides environment variable
        my_Solcast_APIKEY = args.apikey
    if my_Solcast_APIKEY is None:
        print("No apikey defined - set environment variable SOLCAST_API_KEY or provide on command line using --apikey")
        sys.exit(1)
    
    d = todays_date
    tomorrow = d + timedelta(days = 1)
    for_date = tomorrow.strftime("%Y-%m-%d")
    
    my_VisualCrossing_API_KEY = jon_bulman_utilities.Get_Variable("VISUAL_CROSSING_API_KEY",config,my_DEBUG_level)
    os_lat = jon_bulman_utilities.Get_Variable("MY_LATITUDE",config,my_DEBUG_level)
    os_long = jon_bulman_utilities.Get_Variable("MY_LONGITUDE",config,my_DEBUG_level)
    visualcrossingbaseurl = jon_bulman_utilities.Get_Variable("VISUAL_CROSSING_URL",config,my_DEBUG_level)

    if my_VisualCrossing_API_KEY is None:
        print("No Visual Crossing apikey defined - set environment variable VISUAL_CROSSING_API_KEY")
        sys.exit(1)
    if os_lat is None or os_long is None:
        print("No latitude or longitude defined - set environment variable MY_LATITUDE and MY_LONGITUDE")
        sys.exit(1)
    if visualcrossingbaseurl is None:
        print("No Visual Crossing base URL defined - set environment variable VISUAL_CROSSING_URL")
        sys.exit(1)
    visualcrossingurl = visualcrossingbaseurl + str(os_lat) + "," + str(os_long) + "?key=" + my_VisualCrossing_API_KEY

    print("Getting Visual Crossing data for ",for_date)
    print("Latitude ",os_lat," Longitude ",os_long)
    visualcrossing = jon_bulman_weather.GetVisualCrossingWeatherData(visualcrossingurl, for_date, my_DEBUG_level)

    # First get Solcast Data
    print("Getting Solcast data for ",for_date)
    solcast_data = jon_bulman_weather.GetSolcastWeatherData(solcast_url, my_Solcast_APIKEY, for_date, my_DEBUG_level)

    # Now get Forecastsolar data
    forecastsolarbaseurl = jon_bulman_utilities.Get_Variable("FORECASTSOLAR_URL",config,my_DEBUG_level)
    forecastsolar_plane_declination = jon_bulman_utilities.Get_Variable("FORECASTSOLAR_PLANE_DECLINATION",config,my_DEBUG_level)
    forecastsolar_plane_azimuth = jon_bulman_utilities.Get_Variable("FORECASTSOLAR_PLANE_AZIMUTH",config,my_DEBUG_level)
    forecastsolar_installed_kwp = jon_bulman_utilities.Get_Variable("FORECASTSOLAR_INSTALLED_KWP",config,my_DEBUG_level)

    forecastsolar_url = str(forecastsolarbaseurl) + str(os_lat) + "/" + str(os_long) + "/" + str(forecastsolar_plane_declination) + "/" + str(forecastsolar_plane_azimuth) + "/" + str(forecastsolar_installed_kwp)
    print("Getting Forecastsolar data for ",for_date)
    print("Latitude ",os_lat," Longitude ",os_long," Declination ",forecastsolar_plane_declination," Azimuth ",forecastsolar_plane_azimuth," Installed kWp ",forecastsolar_installed_kwp)
    forecastsolar = jon_bulman_weather.GetForecastsolarWeatherData(forecastsolar_url, for_date, my_DEBUG_level)

# Calculate total expected solar for tomorrow
    solar_pv = solar_pv10 = solar_pv90 = 0
    for i, line in enumerate(solcast_data):
        solar_pv   += jon_bulman_weather.Solcast_Breakdown.PV_Estimate(line, None)
        solar_pv10 += jon_bulman_weather.Solcast_Breakdown.PV_Estimate(line, "p10")
        solar_pv90 += jon_bulman_weather.Solcast_Breakdown.PV_Estimate(line, "p90")
    solar_pv /= 2 # After pinging Tim, this is to convert from kW to kWh (each piece of data is per half hour)
    solar_pv10 /= 2 
    solar_pv90 /= 2

    solar_data = Solar_PV_Data(for_date, forecastsolar/1000, solar_pv, visualcrossing)

    if solar_data is not None:        
        # load up weather data
        db_file = output_dir+"/Solar_PV_Data.json" 
        weather_data = jon_bulman_utilities.load_json(db_file, class_lookup["Solar_PV_Data"])

        new_date = solar_data.Date()
        # traverse for all elements
        add = True
        for i, line in enumerate(weather_data):
            date_check = line.Date() 
            if date_check == new_date:
                # already exists - do not add again
                add = False
                break
        if add :
            weather_data.append(solar_data)
            print("Adding..")
            Solar_PV_Data.Print(solar_data)
            # Convert every object in the list to a dict first
            json_compatible_list = [item.to_dict() for item in weather_data]
            # save weather data
            db_file = output_dir+"/Solar_PV_Data.json" 
            with open(db_file, "w") as f_out:
                json.dump(json_compatible_list, f_out, indent=3)
        else:
            print("already exists",new_date)

if __name__ == "__main__":
    main()