import json

import requests


identity = 24427
close_date = '2024-01-30'
comment = 'Ceci est un commentaire de cloture'

url = f"http://127.0.0.1:14975/events/close/{identity}"

headers = {
    'close': close_date,
    'comment': comment
}

response_close = requests.put(url, headers=headers)
print(response_close.status_code)

if response_close.status_code == 400:
    print(response_close.text)

identity = 12
############################################################
response_set_export = requests.put(f"http://127.0.0.1:14975/events/set-exportation/{identity}")
print()
########################################


sitevalue='Forterre'
turbinevalue=12
categoryvalue='PLAN/O&M'

response_get = requests.get(f"http://127.0.0.1:14975/events/search-in-events?site=sitevalue&turbine=turbinevalue&category=categoryvalue")

try:
    response_json = response_get.json()
except json.decoder.JSONDecodeError:
    response_json = None

##############
api_url_post = 'http://127.0.0.1:14975/events/insert'

# Données à envoyer (à adapter selon votre structure JSON)
data_to_insert = {
  "data": {
    "Aggregator": "GAZEL UNIPER",
    "CMMS_Reference": "null",
    "Category": "PLAN/O&M",
    "Close": "2022-09-19 12:00",
    "Comment": "TBS pannes pitch et low oil level. hydraulic\nWO80803",
    "Company": "RES",
    "Contact": "JRT/LCA",
    "Contractual_Indicator": "Penalising",
    "Creation_Timestamp": "null",
    "Employee": "null",
    "Exported_Smart": "null",
    "Group": "WTG Forced",
    "Important_Event": "False",
    "LastUpdate_Timestamp": "null",
    "Market": "france",
    "Open": "2022-09-19 09:00",
    "Ppa_Declaration": "null",
    "Sector": "Secteur Sud Est",
    "Site": "Roussas-Claves",
    "Source": "DailyTracker",
    "SubGroup": "Hub/Pitch System",
    "Supervision": "Laurent",
    "Turbine": "ROU_T09"
  }
}

response_insert = requests.post(api_url_post, json=data_to_insert)
try:
    response_data = response_insert.json()
    print(response_insert.status_code)
    print(response_data)
except requests.exceptions.JSONDecodeError:
    print(response_insert.status_code)
    print(response_insert.text)


#############################


########################################################

api_url = 'http://127.0.0.1:14975/events'
identity = '24427'
response = requests.get(f"{api_url}/{identity}")
###########################################################

#response_delete = requests.delete(f"http://127.0.0.1:14975/events/delete/{identity}")

############################################################
response_set_export = requests.put(f"http://127.0.0.1:14975/events/set-exportation/{identity}")
########################################

#####################################

########################################

response_close = requests.put(f"http://127.0.0.1:14975/events/close/{identity}")



if response.status_code == 200:

    data = response.json()
    print(data)
elif response.status_code == 404:

    print("Aucun événement trouvé.")
elif response.status_code == 500:

    print("Une erreur interne du serveur s'est produite.")
else:
    # Gérer d'autres codes d'état si nécessaire
    print(f"Réponse inattendue: {response.status_code}")


