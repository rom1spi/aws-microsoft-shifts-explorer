import json
import notifier

def manageResponse(statusCode, message, notify=True):
    response = {
        "statusCode": statusCode,
        "body": json.dumps(message),
        "isBase64Encoded": False
    }
    if notify:
        notifier.notify(statusCode, message)
    return response