from pprint import pprint

from api_client import GroundwaterDataLibraryAPI

api = GroundwaterDataLibraryAPI(
    'https://api.nonprod.groundwaterdatalibrary.ga.gov.au/gdl',
    'G55IXmb3qR5SlYDSgmm5n103wlil1vEN3q6aDqFa',
    '6b8tn1jodcb71nkfpqmuc3gbl1',
    '1jfflhsl87i5imbnupgqsg7oiqe7k7gtqbkuhqjle8vkhdac24c2',
)

pprint(api.get_datastore_index())

