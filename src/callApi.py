import hashlib
import time
import requests
import json
from typing import Dict, Any, Union

# --- CONFIGURATION ---
# NOTE: Replace with your actual base URL and shared secret
SHARED_SECRET = '&Cx6)u3`rV9Q^[~NBc8-Hk1b,~h923(U5|r-#hx][tg||36/C}jYX5I>U:KjBhLm'
BASE_API_URL = "https://local.nbinfo.dk/wp-json/mail-list/v1" # [register, confirm, remove]
# ---------------------

def generate_signature(secret: str, timestamp: str, payload_dict: Dict[str, Any]) -> str:
    """
    Generates the SHA-256 signature for the request.

    The signature is calculated by hashing a string created by concatenating:
    1. The SHARED_SECRET
    2. The current UNIX timestamp (as a string)
    3. The canonical JSON string representation of the payload (with sorted keys)

    This consistent concatenation and sorting is CRITICAL for the server to successfully verify the request.
    """
    # Create the canonical (sorted) JSON string from the dictionary
    canonical_payload_string = json.dumps(payload_dict, sort_keys=True)
    
    # Concatenate the elements in the required order
    data_to_sign = f"{secret}{timestamp}{canonical_payload_string}"
    
    # Calculate the SHA-256 hash
    signature = hashlib.sha256(data_to_sign.encode('utf-8')).hexdigest()
    return signature

def send_signed_request(url_suffix: str, payload_json_string: str) -> Union[Dict[str, Any], str]:
    """
    Makes a signed POST request to the API endpoint.

    Args:
        url_suffix: The last part of the API path (e.g., "resource" or "users/create").
        payload_json_string: The data to send, provided as a JSON string.

    Returns:
        The parsed JSON response object (Dict) on success, or an error string on failure.
    """
    
    try:
        # 1. Parse the input JSON string into a Python dictionary
        payload_dict = json.loads(payload_json_string)
    except json.JSONDecodeError:
        return "Error: Invalid JSON payload string provided."
        
    # 2. Prepare authentication elements
    timestamp = str(int(time.time()))
    signature = generate_signature(SHARED_SECRET, timestamp, payload_dict)
    
    # 3. Construct the request
    full_url = f"{BASE_API_URL}/{url_suffix.lstrip('/')}"
    
    headers = {
        "X-Client-Timestamp": timestamp,      # Time for replay attack prevention
        "X-Client-Signature": signature,      # The authenticity hash
        "Content-Type": "application/json"    # Specify JSON format
    }
    
    print(f"-> Sending request to: {full_url}")
    print(f"-> Signature: {signature[:10]}...")
    
    try:
        # Send the dictionary directly via the 'json' parameter of requests
        response = requests.post(full_url, headers=headers, json=payload_dict)
        
        # 4. Handle response status
        if response.status_code == 200:
            # Success: Return the parsed JSON body
            return response.json()
        else:
            # Failure: Return a descriptive error message with the raw response text
            return (f"API Request Failed (Status: {response.status_code}). "
                    f"Server Response: {response.text}")

    except requests.exceptions.ConnectionError:
        return f"Error: Failed to connect to API at {full_url}. Check connectivity and URL."
    except requests.exceptions.RequestException as e:
        return f"An unexpected error occurred during the request: {e}"

# --- EXAMPLE USAGE ---

# 1. Define the API path and the data payload
TS = str(int(time.time()))
api_path = "register"
data_to_send = json.dumps({
    "email": "nb@svaneke.net",
    "timestamp": TS # Note: This timestamp is part of the DATA, not the header/signature
})

# 2. Call the function
result = send_signed_request(api_path, data_to_send)

# 3. Print the result
if isinstance(result, str) and result.startswith("Error"):
    print("\n--- ERROR ---")
    print(result)
else:
    print("\n--- API RESPONSE ---")
    print(json.dumps(result, indent=4))
    
# --- END OF EXAMPLE USAGE ---
