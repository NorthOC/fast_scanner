import json
import requests
from datetime import datetime as date
from time import sleep

class FastScanner:
    COUNTRY_CODE_API = 'https://gist.githubusercontent.com/anubhavshrimal/75f6183458db8c453306f93521e93d37/raw/f77e7598a8503f1f70528ae1cbf9f66755698a16/CountryCodes.json'
    HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}


    def __init__(self):
        self.from_country = {}
        self.to_country = {}
        self.from_airport = {}
        self.to_airport = {}
        self.flight_details = []

    def scan(self, calendar_scan = False) -> None:
        """Main function.\n
        calendar_scan: Extensively scans the flight calendar for all recorded flight possibilies to a specific destination starting from current month (default scans prices only for the cheapest month)"""
        self.from_country = self.select_from_country()
        self.to_country = self.select_to_country()
        self.to_airport = self.select_to_airport()
        self.from_airport = self.select_from_airport()

        if calendar_scan == True:
            # custom functionality to scan the full calendar of a flight to a specific destination
            self.flight_details = self.scan_calendar()
        else:
            self.flight_details = self.select_flight_dates()
        self.output_flight_url()

    def select_from_country(self) -> dict:
        # Request country codes
        res = requests.get(FastScanner.COUNTRY_CODE_API, headers=FastScanner.HEADERS)
        countries = json.loads(res.text)
        while True:
            search = str(input("Enter your country code or country name: ")).strip().lower()
            for country in countries:
                if country["code"].lower() == search or country["name"].lower() == search:
                    # add country object as class instance variable
                    print(country)
                    return country
            print("Country code not found. Try again.")

    def select_to_country(self) -> dict:
        from_country_code = self.from_country['code']
        #skyscanner API
        api_url = f'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{from_country_code}/anywhere/anytime/anytime/?apikey=8aa374f4e28e4664bf268f850f767535'
        res = requests.get(api_url, headers=FastScanner.HEADERS)
        data = self.parse_skyscanner_api(json.loads(res.text))

        self.print_api_results(data)

        country_name = self.from_country["name"]

        while True:
            selected_id = int(input(f"Select country you want to fly to from {country_name} (enter number): ")) - 1
            if selected_id in range(0,len(data["PlacePrices"])):
                break
        data["PlacePrices"].reverse()

        print(data["PlacePrices"][selected_id])
        return data["PlacePrices"][selected_id]
    
    def parse_skyscanner_api(self, data) -> dict:
        # All objects are stored in PlacePrices in API
        data["PlacePrices"].sort(key=self.sort_func, reverse=True)
        for i in data["PlacePrices"].copy():
            # In case there is no price
            if "DirectPrice" not in i and "IndirectPrice" not in i:
                price = 0
            # In case there are both direct and indirect prices, pick the cheaper one
            elif "DirectPrice" in i and "IndirectPrice" in i:
                price_direct = i['DirectPrice']
                price_indirect = i["IndirectPrice"]
                if price_direct <= price_indirect:
                    price = price_direct
                else:
                    price = price_indirect
            elif "DirectPrice" not in i:
                price = i["IndirectPrice"]
            elif "IndirectPrice" not in i:
                price = i['DirectPrice']
            # remove country if price is 0
            if price == 0:
                data["PlacePrices"].remove(i)
        return data
    
    def print_api_results(self, data: dict) -> None:

        count = len(data["PlacePrices"])
        for i in data["PlacePrices"]:
            price = 0
            is_direct = False
            if "DirectPrice" not in i:
                price = i["IndirectPrice"]
            elif "IndirectPrice" not in i:
                price = i['DirectPrice']
                is_direct = True
            elif i['IndirectPrice'] < i["DirectPrice"]:
                price = i['IndirectPrice']
            else:
                price = i['DirectPrice']
                is_direct = True

            print((str(count) + " ").ljust(5) + i["Name"].ljust(25), end=" ")
            # cheapest flight for to country could be either direct or indirect
            if is_direct:
                print(str(price) + " Eur  DIRECT_FLIGHT")
            else:
                print(str(price) + " Eur  INDIRECT")
            count-=1
    
    def select_to_airport(self) -> dict:
        if self.from_country == {}:
            self.select_from_country()
        if self.to_country == {}:
            self.select_to_country()
        
        # outbound country code is received from a non skyscanner API (that is why the keys are different)
        from_country_code = self.from_country['code'].upper()
        to_country_code = self.to_country['Id']
        #skyscanner API
        api_url = f'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{from_country_code}/{to_country_code}/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=false'
        res = requests.get(api_url, headers=FastScanner.HEADERS)

        data = self.parse_skyscanner_api(json.loads(res.text))

        self.print_api_results(data)

        country_name = self.to_country["Name"]

        while True:
            selected_id = int(input(f"Select an airport in {country_name} you want to fly to (enter number): ")) - 1
            if selected_id in range(0,len(data["PlacePrices"])):
                break
        data["PlacePrices"].reverse()

        print(data["PlacePrices"][selected_id])
        return data["PlacePrices"][selected_id]

    def select_from_airport(self) -> dict:
        #skyscanner API
        from_country_code = self.from_country['code'].upper()
        to_airport_code = self.to_airport["Id"]
        api_url = f'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/origins/{from_country_code}/{to_airport_code}/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=false'
        res = requests.get(api_url, headers=FastScanner.HEADERS)

        data = self.parse_skyscanner_api(json.loads(res.text))

        self.print_api_results(data)

        country_name = self.from_country['name']

        while True:
            selected_id = int(input(f"Select an airport in {country_name} you want to fly from (enter number): ")) - 1
            if selected_id in range(0,len(data["PlacePrices"])):
                break
        data["PlacePrices"].reverse()

        print(data["PlacePrices"][selected_id])
        return data["PlacePrices"][selected_id]
    
    def select_flight_dates(self) -> dict:
        """Scans only the cheapest month (deemed by Skyscanner) for prices to a specific destination"""
        from_airport_code = self.from_airport["Id"]
        to_airport_code = self.to_airport["Id"]
        api_url = f'https://www.skyscanner.net/g/monthviewservice/LT/EUR/en-GB/calendar/{from_airport_code}/{to_airport_code}/cheapest/cheapest/?abvariant=rts_who_precompute:a&apikey=6f4cb8367f544db99cd1e2ea86fb2627'
        
        res = requests.get(api_url, headers=FastScanner.HEADERS)
        data = json.loads(res.text)

        found_flights = []
        for x in data["PriceGrids"]["Grid"]:
            for y in x:
                if "Direct" not in y and "Indirect" not in y:
                    continue

                keys = []
                if "Direct" in y:
                    keys.append("Direct")
                if "Indirect" in y:
                    keys.append("Indirect")

                for key in keys:
                    trace_refs = y[key]["TraceRefs"]
                    from_flight_info = data["Traces"][trace_refs[0]].split("*")
                    to_flight_info = data["Traces"][trace_refs[1]].split("*")
                    flight = {}
                    flight["price"] = y[key]["Price"]
                    flight["from_info"] = from_flight_info
                    flight["to_info"] = to_flight_info
                    found_flights.append(flight)

        found_flights.sort(key=self.flight_sort, reverse=True)
        count = len(found_flights)
        for flight in found_flights:
            flight_type = "DIRECT"
            if flight["from_info"][1] != 'D' or flight["to_info"][1] != 'D':
                flight_type = "INDIRECT"

            from_date = date.strptime(flight["from_info"][4],"%Y%m%d").strftime("%d/%m/%Y")
            to_date = date.strptime(flight["to_info"][4],"%Y%m%d").strftime("%d/%m/%Y")


            print((str(count) + ".").ljust(5), flight["price"], "Eur", flight_type, "("+from_airport_code+" - "+to_airport_code+")",from_date, "-" ,to_date)
            count-=1

        while True:
            try:
                selected_id = int(input(f"Select your flight date (enter a number): ")) - 1
            except ValueError:
                continue
            if selected_id in range(0,len(found_flights)):
                break
        found_flights.reverse()

        #print(found_flights[selected_id])

        return found_flights[selected_id]

    def scan_calendar(self) -> dict:
        """Extensively scans the flight calendar for all recorded flight possibilies to a specific destination starting from current month"""
        from_airport_code = self.from_airport["Id"]
        to_airport_code = self.to_airport["Id"]
        from_date = date.today().strftime("%Y-%m")
        to_date = date.today().strftime("%Y-%m")

        from_date_list = from_date.split("-")
        from_month = from_date_list[1]
        from_year = from_date_list[0]
        from_date_obj = {}
        from_date_obj["month"] = from_month
        from_date_obj["year"] = from_year

        to_date_list = to_date.split("-")
        to_month = to_date_list[1]
        to_year = to_date_list[0]
        to_date_obj = {}
        to_date_obj["month"] = to_month
        to_date_obj["year"] = to_year

        min_run_count = 6
        data = {}
        data["Traces"] = ""

        found_flights = []
        while len(data["Traces"]) != 0 or min_run_count > 1:
            min_run_count -= 1
            from_date = from_date_obj["year"] + "-" + from_date_obj["month"]
            to_date = to_date_obj["year"] + "-" + to_date_obj["month"]
            print(f"Scanning flight prices for flight {from_airport_code}-{to_airport_code}:", from_date, "-", to_date)
            
            api_url = f'https://www.skyscanner.net/g/monthviewservice/LT/EUR/en-GB/calendar/{from_airport_code}/{to_airport_code}/{from_date}/{to_date}/?abvariant=rts_who_precompute:a&apikey=6f4cb8367f544db99cd1e2ea86fb2627'
            res = requests.get(api_url, headers=FastScanner.HEADERS)
            data = json.loads(res.text)
            sleep(1.5)

            for x in data["PriceGrids"]["Grid"]:
                for y in x:
                    if "Direct" not in y and "Indirect" not in y:
                        continue

                    keys = []
                    if "Direct" in y:
                        keys.append("Direct")
                    if "Indirect" in y:
                        keys.append("Indirect")

                    for key in keys:
                        trace_refs = y[key]["TraceRefs"]
                        from_flight_info = data["Traces"][trace_refs[0]].split("*")
                        to_flight_info = data["Traces"][trace_refs[1]].split("*")
                        flight = {}
                        flight["price"] = y[key]["Price"]
                        flight["from_info"] = from_flight_info
                        flight["to_info"] = to_flight_info
                        found_flights.append(flight)

            if int(to_date_obj['month']) == int(from_date_obj['month']):
                to_date_obj = self.increment_month(to_date_obj)
            else:
                from_date_obj = self.increment_month(from_date_obj)
            #print(data)

        found_flights.sort(key=self.flight_sort, reverse=True)
        count = len(found_flights)
        for flight in found_flights:
            flight_type = "DIRECT"
            if flight["from_info"][1] != 'D' or flight["to_info"][1] != 'D':
                flight_type = "INDIRECT"

            from_date = date.strptime(flight["from_info"][4],"%Y%m%d").strftime("%d/%m/%Y")
            to_date = date.strptime(flight["to_info"][4],"%Y%m%d").strftime("%d/%m/%Y")

            print((str(count) + ".").ljust(5), flight["price"], "Eur", flight_type, "("+from_airport_code+" - "+to_airport_code+")",from_date, "-" ,to_date)
            count-=1

        while True:
            try:
                selected_id = int(input(f"Select your flight date (enter a number): ")) - 1
            except ValueError:
                continue
            if selected_id in range(0,len(found_flights)):
                break
        found_flights.reverse()

        #print(found_flights[selected_id])

        return found_flights[selected_id]
    
    def output_flight_url(self) -> None:
        from_airport_code = self.from_airport["Id"]
        to_airport_code = self.to_airport["Id"]
        # format date to proper url
        from_date = self.flight_details["from_info"][4][2:]
        to_date = self.flight_details["to_info"][4][2:]
        flight_url = f"https://www.skyscanner.net/transport/flights/{from_airport_code}/{to_airport_code}/{from_date}/{to_date}/"
        print (f"Flight url: {flight_url}")
    
    def sort_func(self, e):
        # for sorting results from Skycanner API
        if "DirectPrice" not in e and "IndirectPrice" not in e:
            return 0
        if "DirectPrice" not in e:
            return e["IndirectPrice"]
        if "IndirectPrice" not in e:
            return e['DirectPrice']
        if e['IndirectPrice'] < e["DirectPrice"]:
            return e['IndirectPrice']
        return e['DirectPrice']
    
    def flight_sort(self, e):
        return e['price']
    
    def increment_month(self, date):
        month_num = int(date["month"]) + 1
        if month_num > 12:
            date["month"] = "01"
            date["year"] = str(int(date["year"]) + 1)
        elif month_num < 10:
            date["month"] = "0"+str(month_num)
        else:
            date["month"] = str(month_num)
        return date
    
        
scanner = FastScanner()
scanner.scan(calendar_scan=False)
