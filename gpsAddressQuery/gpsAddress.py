from geopy.geocoders import Nominatim


class Address:

    def __init__(self, country, state_region, county_province, city):
        self.country = country
        self.state_region = state_region
        self.county_province =county_province
        self.city = city

    @classmethod
    def build(self, lat, lng):
        self = gpsToAddress(lat, lng)


    country = None
    state_region = None
    county_province = None
    city = None

    def toString(self):
        UNKNOWN = "<unknown>"
        str = u'';
        if(self.country != None):
            str = str.join( self.country + "\t" )
        else: str.join(UNKNOWN+"\t")

        if (self.state_region != None):
            str += self.state_region + "\t"
        else: str += UNKNOWN+"\t"

        if (self.county_province != None):
            str += self.county_province + "\t"
        else: str+=UNKNOWN+"\t"

        if (self.city != None):
            str += self.city + "\t"
        else: str +=UNKNOWN+"\t"

        return str


def gpsToAddress(lat, lng):
    if(lat != None and lng != None):
        geolocator = Nominatim()
        location = geolocator.reverse(lat + ", " + lng)

        address = None
        if "address" in location.raw.keys():
            address = location.raw["address"]
            if("country" in address.keys()):
                country = address["country"]
            else: country = None

            if("state" in address.keys()):
                state_region = address["state"]
            else: state_region = None

            if ("county" in address.keys()):
                county_province = address["county"]
            else: county_province = None


            if("city" in address.keys()):
                city = address["city"]
            elif ("town" in address.keys()):
                city = address["town"]
            else: city=None

            address = Address(country, state_region, county_province, city)
        return address


