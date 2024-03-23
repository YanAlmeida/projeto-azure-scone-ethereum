import requests
import json
import pytz
from datetime import datetime

API_KEY = 'API_KEY'
ACCOUNT_ID = 4269971
FUNCTION_NAME = 'OtherTransaction/Function/src.thread_accept_connection:process_pdf_data'

def query_trace_durations(starting_time: str, ending_time: str):
    """
    Queries New Relic for trace durations of a specific function within a specified time period.
    
    :param starting_time: The starting time of the period to query, in UTC-3 (São Paulo time)
    :param ending_time: The ending time of the period to query, in UTC-3 (São Paulo time)
    :return: JSON data of query results
    """
    # Convert São Paulo time (UTC-3) to UTC
    sao_paulo = pytz.timezone('America/Sao_Paulo')
    utc = pytz.utc

    start_dt = sao_paulo.localize(datetime.strptime(starting_time, '%Y-%m-%d %H:%M:%S')).astimezone(utc)
    end_dt = sao_paulo.localize(datetime.strptime(ending_time, '%Y-%m-%d %H:%M:%S')).astimezone(utc)

    # Format times in ISO 8601 format for the query
    start_time_utc = start_dt.timestamp() * 1000
    end_time_utc = end_dt.timestamp() * 1000
    
    # The GraphQL endpoint
    url = 'https://api.newrelic.com/graphql'

    # The query, using NRQL
    # Ensure your NRQL query is on a single line to avoid formatting issues
    nrql_query = f"FROM Transaction SELECT duration WHERE name = '{FUNCTION_NAME}' AND tags.accountId = '{ACCOUNT_ID}' SINCE {int(start_time_utc)} UNTIL {int(end_time_utc)} LIMIT 5000"
    
    # Construct the full GraphQL query
    query = {
      "query": f'''
        {{
          actor {{
            account(id: {ACCOUNT_ID}) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
      '''
    }

    # Headers with the API key
    headers = {
        'Content-Type': 'application/json',
        'API-Key': API_KEY,
    }

    # Sending the request
    response = requests.post(url, headers=headers, json=query)  # Use json parameter to automatically encode dict to JSON

    # Check response status
    if response.status_code == 200:
        # Return parsed JSON data
        return response.json()['data']['actor']['account']['nrql']['results']
    else:
        print("Failed to retrieve data:", response.status_code)
        return None

def process_text_to_dict_corrected(text):
    lines = text.strip().split('\n')
    test_dict = {}

    for line in lines:
        if line.startswith('START') or line.startswith('END'):
            parts = line.split(': ', 1)  # Correct split to include space
            key_value = parts[0].split(' ', 1)
            key = key_value[1].strip()
            if key not in test_dict:
                test_dict[key] = [None, None]
            if line.startswith('START'):
                test_dict[key][0] = parts[1].strip()
            else:
                test_dict[key][1] = parts[1].strip()

    # Convert list to tuple for final output
    for key in test_dict:
        test_dict[key] = tuple(test_dict[key])

    return test_dict

filename = "/tmp/DADOS_TESTES.txt"

with open(filename, 'r') as file:
    total_data = file.read()

tempos = process_text_to_dict_corrected(total_data)

resultados = {}
for k, v in tempos.items():
    resultados[k] = query_trace_durations(*v)

import json
import os


filename = f"/tmp/{list(tempos.keys())[0]}/RESULTADOS_TESTES_TEE.txt"

with open(filename, 'a') as file:
    file.write(json.dumps(resultados))
filename

os.rename("/tmp/DADOS_TESTES.txt", f"/tmp/{list(tempos.keys())[0]}/DADOS_TESTES.txt")
