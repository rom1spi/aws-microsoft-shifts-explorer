import json
import requests
import time
import datetime
import re
from responseManager import manageReponse
from authentificationManager import get_secret

_TENANT_ID="7aee3959-8726-4982-8d9b-7967b3cdf3d7"
_TEAM_ID="15e62f50-7d7c-482e-a657-5d344b19f782"
_SECRET_KEY="9e23.e-MSUTy5y=IYNAamOGaPhtOYdk@"
_CLIENT_ID="26f8af2d-f647-4427-925b-2ac8c3059a73"

_SHIFT_NAME_PATTERN = "(?i)astreinte"

def getShiftsUsersForPeriod(event, context):
    regex="."
    if _SHIFT_NAME_PATTERN:
        regex=_SHIFT_NAME_PATTERN
    pattern = re.compile(regex)
    token=json.loads(getToken())

    shifts_response=json.loads(getShifts(token["access_token"],event))
    #print(json.dumps(shifts_response))
    shifts=shifts_response["value"]
    #print(json.dumps(shifts))

    shifts_users_list=[]
    for shift in shifts:
        #print(json.dumps(shift))
        #print(shift["sharedShift"]["displayName"])
        match=pattern.match(str(shift["sharedShift"]["displayName"]))
        if match != None and shift["userId"] not in shifts_users_list:
            shift_user={
                "userId": shift["userId"],
                "shiftName": shift["sharedShift"]["displayName"],
                "startDateTime": shift["sharedShift"]["startDateTime"],
                "endDateTime": shift["sharedShift"]["endDateTime"],
            }
            shifts_users_list.append(shift_user)

    print(json.dumps(shifts_users_list))

    email_list=[]
    start_time = time.time()
    for user_shift in shifts_users_list:
        user_details=getUserById(token["access_token"], user_shift["userId"])
        #print(json.dumps(user))
        userdata=json.loads(user_details)
        email_list.append([userdata["mail"],userdata["displayName"],user_shift["shiftName"],user_shift["startDateTime"],user_shift["endDateTime"]])
        #print(json.dumps(email_list))

    #print("--- loop2: %s seconds ---" % (time.time() - start_time))
    #print(json.dumps(email_list))

    body = {
        "input": event,
        "message": email_list
    }

    return manageReponse(200,json.dumps(body), False)

"""
    {
        "filters": {
            "nextWeekday": "TUE"
        }
    }
"""
def getShiftsUsersForNextWeekDay(event, context):
    weekday=getWeekDayNum(str(event["filters"]["nextWeekday"]))
    now = datetime.datetime.now()
    d = datetime.date(now.year, now.month, now.day)
    next_period_fullday = next_weekday(d, weekday) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    print(next_period_fullday)
    nextday=next_period_fullday + datetime.timedelta(days=1)
    print(nextday)

    input={
        "sharedShiftPeriod": {
            "startDateTime": str(next_period_fullday) + "T00:00:00.000Z",
            "endDateTime": str(nextday) + "T00:00:00.000Z"
        }
    }

    return getShiftsUsersForPeriod(input, context)

def getShifts(token,event):
    url = "https://graph.microsoft.com/beta/teams/"+_TEAM_ID+"/schedule/shifts"
    startDateTime = str(event["sharedShiftPeriod"]["startDateTime"])
    endDateTime = str(event["sharedShiftPeriod"]["endDateTime"])
    # querystring = {"$filter":"sharedShift/startDateTime%20ge%202019-12-05T00:00:00.000Z%20and%20sharedShift/endDateTime%20le%202019-12-06T00:00:00.000Z"}
    querystring = {"$filter":"sharedShift/startDateTime ge " + startDateTime + " and sharedShift/endDateTime le " + endDateTime}

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
    url = "https://graph.microsoft.com/beta/users/"+userId

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
    print(json.dumps(secret))
    url = "https://login.microsoftonline.com/"+_TENANT_ID+"/oauth2/v2.0/token"

    payload = "grant_type=password&client_id=" + _CLIENT_ID + "&client_secret=" + _SECRET_KEY + "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&userName=" + secret["username"] + "&password=" + secret["password"]
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