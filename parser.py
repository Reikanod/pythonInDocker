import sys
import json

def show_res(api_id, api_hash, password):
    result = {
        "api_id": api_id,
        "api_hash": api_hash,
        "pass": password
    }

    return result