import os
import requests
import time

trello_api_key = os.environ.get("TRELLO_API_KEY", None)
trello_api_token = os.environ.get("TRELLO_API_TOKEN", None)

if not trello_api_key:
    print("trello_api_key not found")
    exit(0)

if not trello_api_token:
    print("trello_api_token not found")
    exit(0)


class TrelloParent:
    def __init__(self):
        self.payload = {}
        self.headers = {"Accept": "application/json"}
        self.params = {"key": trello_api_key, "token": trello_api_token}
        self.url = "https://api.trello.com/"
        self.success_codes = [200, 201, 203]

    def validate_response_status(self, response):
        if response.status_code not in self.success_codes:
            print("An error occurred.\nResponse status code : ", response.status_code)
            print(response.text)
            exit(0)

    def trello_api_response(self, endpoint, payload_data=None, request_type="GET", batch_request=False):
        request_url = self.url + endpoint
        payload = self.payload.copy()
        params = self.params.copy()
        if batch_request:
            print(f"Performing batch request to {request_url}")
        else:
            print(f"Making {request_type} to {request_url}")
        start_time = time.time()
        if payload_data:
            payload.update(payload_data)
            params.update(payload_data)
        if request_type == "PUT":
            response = requests.put(request_url, headers=self.headers, params=params)
        elif request_type == "POST":
            response = requests.post(request_url, headers=self.headers, params=params)
        elif request_type == "DELETE":
            response = requests.delete(request_url, params=params)
        else:
            response = requests.get(request_url,headers=self.headers, params=params)
        print(f"API call completed in {round(time.time() - start_time, 4)} seconds")

        if batch_request:
            return self.validate_batch_requests_response(response)

        self.validate_response_status(response)
        return response.json()

    def validate_batch_requests_response(self, api_response):
        print("validating batch requests response")
        trello_data = []
        response = api_response.json()
        if not isinstance(response, list):
            print("An error occurred.\nResponse type is not list. type is ", type(response))
            exit(0)
        for single_url_response in response:
            if not isinstance(single_url_response, dict):
                print("An error occurred.\nsingle_url_response type is not dict. type is ", type(single_url_response))
                exit(0)
            dict_key: str = list(single_url_response.keys())[0]
            if dict_key.isdigit():
                status_code = int(dict_key)
            else:
                print("Invalid status code")
                print(single_url_response)
                exit(0)
            if status_code not in self.success_codes:
                print("An error occurred.\nResponse status code for single_url_response: ", status_code)
                exit(0)
            data = single_url_response[dict_key]
            if isinstance(data, list):
                trello_data.extend(data)
            else:
                trello_data.append(data)
        return trello_data

    def perform_trello_action(self, argument, endpoint):
        if isinstance(argument, list):
            if len(argument) == 1:
                trello_id = argument[0]
            else:
                batch_endpoint = "1/batch"
                separator = ','
                urls = []
                for trello_id_ in argument:
                    api_endpoint = endpoint.split("1")[1]
                    urls.append(api_endpoint.format(trello_id_))
                all_urls = (separator.join(urls))
                return self.trello_api_response(batch_endpoint, payload_data={"urls": all_urls}, batch_request=True)
        else:
            trello_id = argument
        return self.trello_api_response(endpoint.format(trello_id))
