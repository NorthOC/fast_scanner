import json
import requests
from datetime import datetime as date

#APIs

# search all URL: COUNTRY - ANYWHERE (ANYTIME)
# https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{COUNTRY}/anywhere/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false

# after selecting specific country: COUNTRY - DESTINATION (ANYTIME)
# https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{COUNTRY}/{destination}/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false

# Load specific country airports
# https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{COUNTRY}/{DEST_COUNTRY}/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false


class Skyscanner:
    COUNTRY_CODE_API = 'https://gist.githubusercontent.com/anubhavshrimal/75f6183458db8c453306f93521e93d37/raw/f77e7598a8503f1f70528ae1cbf9f66755698a16/CountryCodes.json'
    HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}


    def __init__(self):
        # Outbound is where you are flying from and inbound is where are you flying to.
        self.from_country = {}
        self.to_country = {}
        self.from_airport = {}
        self.to_airport = {}
        self.flight_details = []

    def scan(self):
        # Run function
        # This is the standard Skyscanner workflow
        self.select_from_country()
        self.select_to_country()
        self.select_to_airport()
        self.select_from_airport()
        self.output_flight_dates()
        self.output_flight_url()

    def select_from_country(self):
        # Select a country code from an API
        res = requests.get(Skyscanner.COUNTRY_CODE_API, headers=Skyscanner.HEADERS)
        countries = json.loads(res.text)
        while True:
            search = str(input("Enter your country code: ")).strip().upper()
            for country in countries:
                if country["code"] == search:
                    self.from_country = country
                    return 0
            print("Country code not found. Try again.")

    def select_to_country(self):
        print(self.from_country)
        from_country_code = self.from_country['code'].upper()
        #skyscanner API
        api_url = f'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{from_country_code}/anywhere/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=false'
        res = requests.get(api_url, headers=Skyscanner.HEADERS)

        data = self.parse_skyscanner_api(json.loads(res.text))

        self.print_api_results(data)

        while True:
            selected_id = int(input(f"Select country you want to fly to (enter number): ")) - 1
            if selected_id in range(0,len(data["PlacePrices"])):
                break
        data["PlacePrices"].reverse()

        print(data["PlacePrices"][selected_id])
        self.to_country = data["PlacePrices"][selected_id]
        return 0
    
    def parse_skyscanner_api(self, data):

        data["PlacePrices"].sort(key=self.sort_func, reverse=True)

        for i in data["PlacePrices"].copy():
            if "DirectPrice" not in i and "IndirectPrice" not in i:
                price = 0
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
                
            if price == 0:
                data["PlacePrices"].remove(i)
        return data
    
    def print_api_results(self, data):

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
    
    def select_to_airport(self):
        if self.from_country == {}:
            self.select_from_country()
        if self.to_country == {}:
            self.select_to_country()
        
        # outbound country code is received from a non skyscanner API (that is why the keys are different)
        from_country_code = self.from_country['code'].upper()
        to_country_code = self.to_country['Id']
        #skyscanner API
        api_url = f'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/destinations/{from_country_code}/{to_country_code}/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=false'
        res = requests.get(api_url, headers=Skyscanner.HEADERS)

        data = self.parse_skyscanner_api(json.loads(res.text))

        self.print_api_results(data)

        while True:
            selected_id = int(input(f"Select an airport you want to fly to (enter number): ")) - 1
            if selected_id in range(0,len(data["PlacePrices"])):
                break
        data["PlacePrices"].reverse()

        print(data["PlacePrices"][selected_id])
        self.to_airport = data["PlacePrices"][selected_id]
        return 0

    def select_from_airport(self):
        #skyscanner API
        from_country_code = self.from_country['code'].upper()
        to_airport_code = self.to_airport["Id"]
        api_url = f'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/UK/EUR/en-GB/origins/{from_country_code}/{to_airport_code}/anytime/anytime/?profile=minimalcityrollupwithnamesv2&include=image;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=false'
        res = requests.get(api_url, headers=Skyscanner.HEADERS)

        data = self.parse_skyscanner_api(json.loads(res.text))

        self.print_api_results(data)

        while True:
            selected_id = int(input(f"Select an airport you want to fly from (enter number): ")) - 1
            if selected_id in range(0,len(data["PlacePrices"])):
                break
        data["PlacePrices"].reverse()

        print(data["PlacePrices"][selected_id])
        self.from_airport = data["PlacePrices"][selected_id]
        return 0
    
    def output_flight_dates(self):
        from_airport_code = self.from_airport["Id"]
        to_airport_code = self.to_airport["Id"]
        api_url = f'https://www.skyscanner.net/g/monthviewservice/LT/EUR/en-GB/calendar/{from_airport_code}/{to_airport_code}/cheapest/cheapest/?abvariant=rts_who_precompute:a&apikey=6f4cb8367f544db99cd1e2ea86fb2627'
        
        res = requests.get(api_url, headers=Skyscanner.HEADERS)
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

            print((str(count) + ".").ljust(5), flight["price"], "Eur", flight_type, from_date, "-" ,to_date)
            count-=1

        while True:
            try:
                selected_id = int(input(f"Select your flight (enter a number): ")) - 1
            except ValueError:
                continue
            if selected_id in range(0,len(found_flights)):
                break
        found_flights.reverse()

        #print(found_flights[selected_id])

        self.flight_details = found_flights[selected_id]


    
    def output_flight_url(self):
        from_airport_code = self.from_airport["Id"]
        to_airport_code = self.to_airport["Id"]
        # format date to proper url
        from_date = self.flight_details["from_info"][4][2:]
        to_date = self.flight_details["to_info"][4][2:]
        flight_url = f"https://www.skyscanner.net/transport/flights/{from_airport_code}/{to_airport_code}/{from_date}/{to_date}/"
        print (f"Flight url: {flight_url}")
        return 0
    
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
        
scanner = Skyscanner()
scanner.scan()

