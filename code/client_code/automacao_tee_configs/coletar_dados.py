import os
from smart_contract import get_contract
from web3 import Web3, Account
from web3.contract import Contract
from web3.eth import Eth
from web3._utils.filters import LogFilter
from hdwallet import HDWallet
import requests


def get_test_identifier(url):
    identifier = url.split('/')[-1].split('?')
    return identifier[0].strip('output_').strip('.pdf') + '-' + identifier[1]

from concurrent.futures import ThreadPoolExecutor

def split(list_a: list, chunk_size: int):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]

def get_jobs(chunk_size):
    jobs_ids = get_contract(999).returnJobsIds()

    pairs = split(jobs_ids, chunk_size)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(get_contract(999).getJobs, pair) for pair in pairs]

        # Optionally, wait for all futures to complete and process results
        final_result = []
        for future in futures:
            try:
                # Get the result of the future. This line will block until the future is complete
                final_result += future.result()
                # Process result (if needed)
            except Exception as e:
                print(f"Request failed: {e}")
        return final_result

from collections import defaultdict
from functools import partial
import json
import time

test_identifier = os.environ.get('TEST_IDENTIFIER')

results = defaultdict(partial(defaultdict, list))
times = defaultdict(partial(defaultdict, int))

CHUNK_SIZE = 50

a = time.time()
jobs = get_jobs(CHUNK_SIZE)
print(time.time() - a)

for job in jobs:
    if job['processedTimestamp'] != 0:
        message = 'SUCESSO'
    else:
        message = 'ERRO'
    
    results[test_identifier][message].append(job['processedTimestamp'] - job['startingTimestamp'])
    if times[test_identifier]['START'] == 0:
        times[test_identifier]['START'] = 1000000000000
    times[test_identifier]['START'] = min(times[test_identifier]['START'], job['startingTimestamp'])
    times[test_identifier]['END'] = max(times[test_identifier]['END'], job['processedTimestamp'])
print(len(jobs))

from datetime import datetime
import pytz

filename = f"/tmp/DADOS_TESTES.txt"

def timestamp_to_string(timestamp):
    datetime_value = datetime.fromtimestamp(timestamp, tz=pytz.timezone('America/Sao_Paulo'))
    return datetime_value.strftime("%Y-%m-%d %H:%M:%S")


with open(filename, 'a') as file:
    for test, tempos in times.items():
        for marcacao, tempo in tempos.items():
            file.write(f'{marcacao} {test}: {timestamp_to_string(tempo)}\n')
            if marcacao == 'END':
                file.write('#\n')

import json


filename = f"/tmp/{test_identifier}/RESULTADOS_TESTES_BLOCKCHAIN.txt"

with open(filename, 'a') as file:
    file.write(json.dumps(results))


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


filename = f"/tmp/{test_identifier}/RESULTADOS_TESTES_TEE.txt"

with open(filename, 'a') as file:
    file.write(json.dumps(resultados))
filename

os.rename("/tmp/DADOS_TESTES.txt", f"/tmp/{test_identifier}/DADOS_TESTES.txt")
