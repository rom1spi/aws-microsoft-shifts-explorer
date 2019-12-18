import json
import requests
import time
import datetime
import re
from responseManager import manageResponse
from authentificationManager import get_secret

_MICROSOFT_GRAPH_API_VERSION="beta" # beta | v1.0 | ...
_DEFAULT_TIME="T00:00:00.000Z"

g_team_id=None
g_start_datetime=None
g_end_datetime=None
g_shift_name_pattern=None
g_microsoft_graph_api_token=None

"""
    Returns users shifts planned over a period
"""
def getShiftsUsersForPeriod(event, context):
    getTokenResponse = getToken()
    if getTokenResponse is None:
        return manageResponse(407, "Unable to get credentials in AWS Secrets Manager")
    elif "error" in getTokenResponse:
        print(getTokenResponse)
        return manageResponse(407,getTokenResponse)
    token=json.loads(getTokenResponse)
    global g_microsoft_graph_api_token
    g_microsoft_graph_api_token=token["access_token"]

    shifts_response=json.loads(getShifts(g_microsoft_graph_api_token,event))
    if "error" in shifts_response:
        print(json.dumps(shifts_response))
        return manageResponse(407,json.dumps(shifts_response))
    shifts=shifts_response["value"]

    # get the pattern to filter on shifts names
    regex="."
    global g_shift_name_pattern
    g_shift_name_pattern=event["filters"]["shiftNamePattern"]
    if g_shift_name_pattern:
        regex=g_shift_name_pattern
    pattern = re.compile(regex)

    shifts_users_list=[]
    for shift in shifts:
        match=pattern.match(str(shift["sharedShift"]["displayName"]))
        if match != None and shift["userId"] not in shifts_users_list:
            shift_user={
                "userId": shift["userId"],
                "shiftName": shift["sharedShift"]["displayName"],
                "startDateTime": shift["sharedShift"]["startDateTime"],
                "endDateTime": shift["sharedShift"]["endDateTime"],
            }
            shifts_users_list.append(shift_user)

    userdata_list=[]
    start_time = time.time()
    for user_shift in shifts_users_list:
        user_details=getUserById(g_microsoft_graph_api_token, user_shift["userId"])
        #print(json.dumps(user))
        userdata=json.loads(user_details)
        userdata_json={
            "email": userdata["mail"],
            "displayName": userdata["displayName"],
            "shiftName": user_shift["shiftName"],
            "startDateTime": user_shift["startDateTime"],
            "endDateTime": user_shift["endDateTime"]
        }
        userdata_list.append(userdata_json)
        #print(json.dumps(email_list))

    print(json.dumps(userdata_list))

    return manageResponse(200,userdata_list, False)

"""
    Returns users shifts planned on the next given week day
"""
def getShiftsUsersForNextWeekDay(event, context):
    weekday=getWeekDayNum(str(event["filters"]["nextWeekday"]))
    now = datetime.datetime.now()
    d = datetime.date(now.year, now.month, now.day)
    next_period_fullday = next_weekday(d, weekday) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    nextday=next_period_fullday + datetime.timedelta(days=1)

    input={
        "filters": {
            "sharedShiftPeriod": {
                "startDateTime": str(next_period_fullday) + _DEFAULT_TIME,
                "endDateTime": str(nextday) + _DEFAULT_TIME
            },
            "shiftNamePattern": event["filters"]["shiftNamePattern"]
        }
    }

    return getShiftsUsersForPeriod(input, context)

def getShifts(token,event):
    url = "https://graph.microsoft.com/" + _MICROSOFT_GRAPH_API_VERSION + "/teams/"+g_team_id+"/schedule/shifts"
    global g_start_datetime
    global g_end_datetime
    g_start_datetime = str(event["filters"]["sharedShiftPeriod"]["startDateTime"])
    g_end_datetime = str(event["filters"]["sharedShiftPeriod"]["endDateTime"])
    querystring = {"$filter":"sharedShift/startDateTime ge " + g_start_datetime + " and sharedShift/endDateTime le " + g_end_datetime}

    headers = {
        'Authorization': "Bearer " + token,
        'User-Agent': "PostmanRuntime/7.20.1",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "16663a6a-b9f7-4931-8420-7737a0af2c28,91a876d6-c665-4334-be53-aa52d4f3b4a5",
        'Host': "graph.microsoft.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text

def getUserById(token, userId):
    url = "https://graph.microsoft.com/" + _MICROSOFT_GRAPH_API_VERSION + "/users/"+userId

    headers = {
        'SdkVersion': "postman-graph/v1.0",
        'Authorization': "Bearer " + token,
        'User-Agent': "PostmanRuntime/7.20.1",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "daffbf92-9c69-453c-9c28-e18efeb69fc0,2e6b998e-359f-42d4-b327-9d17e8d081d0",
        'Host': "graph.microsoft.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers)
    return response.text

def getToken():    
    secret=get_secret()
    if secret is None:
        return None
    secret_values=json.loads(secret)
    global g_team_id
    g_team_id=secret_values["TEAM_ID"]
    url = "https://login.microsoftonline.com/"+secret_values["TENANT_ID"]+"/oauth2/v2.0/token"

    payload = "grant_type=password&client_id=" + secret_values["CLIENT_ID"] + "&client_secret=" + secret_values["SECRET_KEY"] + "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&userName=" + secret_values["USERNAME"] + "&password=" + secret_values["PASSWORD"]
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'SdkVersion': "postman-graph/v1.0",
        'User-Agent': "PostmanRuntime/7.20.1",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "d4574cb5-0671-4d1a-932c-129a038d74c2,9fbbe046-9b9e-4b22-9ed4-7c90ec218d81",
        'Host': "login.microsoftonline.com",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "229",
        'Cookie': "fpc=AhxT_Apjug1Hqp8d1xC446_SHP9kAQAAAFFbfNUOAAAA; x-ms-gateway-slice=prod; stsservicecookie=ests",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    return response.text

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def getWeekDayNum(x):
    return {
        'MONDAY': 0,
        'TUESDAY': 1,
        'WEDNESDAY': 2,
        'THURSDAY': 3,
        'FRIDAY': 4,
        'SATURDAY': 5,
        'SUNDAY': 6,
        'MON': 0,
        'TUE': 1,
        'WED': 2,
        'THU': 3,
        'FRI': 4,
        'SAT': 5,
        'SUN': 6
    }.get(x, 0) 