import notifier

def manageReponse(statusCode, message, notify=True):
    response = {
        "statusCode": statusCode,
        "body": message
    }
    if notify:
        notifier.notify(statusCode, message)
    return response