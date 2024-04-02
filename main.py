import requests
import datetime
import csv
import time
import sys

# For Assignment 7b, use the test_data.csv file
FILENAME = "test_data/test_data.csv"

# For Assignment 9, use the dialup_connection.csv file
FILENAME = "test_data/dialup_connection_buffer.csv"

def send_to_clearinghouse(body):
    x = requests.post('https://9au0x1ibc3.execute-api.us-west-1.amazonaws.com/v1/clearingHouseAPI', json = body)
    return x.text.replace('"','')

def format_request_body(data, mode):
    if mode == "testing":
        token = get_merchant_token(data["clinic_name"], data["expected_response_message"])
    else:
        token = get_merchant_token(data["clinic_name"])
    body = {
        "merchant_name" : str(data["clinic_name"]),
        "merchant_token" : str(token),
        "bank" : str(data["patient_bank"]),
        "cc_num" : str(data["patient_card_number"]),
        "card_type" : "Debit" if len(data["patient_card_number"]) < 6 else "Credit",
        "security_code" : data["patient_card_security_code"],
        "amount" : data["charge_amount"],
        "card_zip" : data["patient_address"].split("|")[1],
        "timestamp" : str(datetime.datetime.now())
    }
    return body

def get_merchant_token(merchant, expected_message=None):
    if expected_message == "Bad Merchant Credentials.":
        return "invalidtoken"
    return "vOCO823"

def read_csv(filename):
    data = []
    columns = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        columns = next(reader)
        for row in reader:
            d = {}
            for i, col in enumerate(columns):
                d[col] = row[i]
            data.append(d)
    return data

def main():
    data = read_csv(FILENAME)

    mode = ''
    if "expected_response_message" in data[0].keys():
        print("Testing Mode Activated!")
        mode = "testing"
    else:
        print("Adapter Mode Activated!")
        mode = "adapter"
    
    flag = False
    counter = 0
    for row in data:
        body = format_request_body(row, mode)
        response = send_to_clearinghouse(body)
        wait = 1
        while response == "Bank Not Available":
            if wait > 5:
                break
            print(f"Error Detected: Bank Not Available - retrying in {wait} sec.")
            time.sleep(wait)
            response = send_to_clearinghouse(body)
            wait *= 2
            
        if mode == "testing":
            if response == row["expected_response_message"]:
                print("Test Passed! Patient: " + str(row["patient_name"]) + "\n   - Response: " + str(row["expected_response_message"]))
            else:
                flag = True
                counter+=1
                print("Test Failed! Patient: " + str(row["patient_name"]) + "\n   - Expected Response:  " + str(row["expected_response_message"]) + "\n   - Actual Response:    " + str(response))
        else:
            print("Patient: " + str(row["patient_name"]) + "\n   - Response: " + str(response))
    
    if flag and mode == 'testing':
        print(str(counter), " Tests Failed!")
    elif not flag and mode == 'testing':
        print("All Tests Passed!")
    
    

if __name__ == '__main__':
    old_stdout = sys.stdout
    log_file = open("merchant_sim.log","w")
    sys.stdout = log_file
    main()
    sys.stdout = old_stdout
    log_file.close()
