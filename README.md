# aws-microsoft-shifts-explorer (Beta)
 A tool to explore Microsoft Shifts data

It is still considered as a Beta version because we use some features of the Microsoft Graph API which are currently in Beta version. 

## Use case
Your organization uses Microsoft Teams, and employees' planing are stored in Microsoft Shifts.
You want to get all users contact information for all shifts filtered by:
- a given period
or
- the next given week day

## Sample Request:

### getShiftsUsersForPeriod
```json
{
    "filters": {
        "sharedShiftPeriod": {
            "startDateTime": "2019-12-17T00:00:00.000Z",
            "endDateTime": "2019-12-18T00:00:00.000Z"
        },
        "shiftNamePattern": "(?i)duty"
    }
}
```

### getShiftsUsersForNextWeekDay
```json
{
    "filters": {
        "nextWeekday": "TUE",
        "shiftNamePattern": "(?i)duty"
    }
}
```

Possible values for `nextWeekday`: 
`MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`, `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `SUN`

## Sample Response:
```json
{
  "statusCode": 200,
  "body": [
    {
      "email": "romain.spinelli@foo.bar",
      "displayName": "Romain Spinelli",
      "shiftName": "Cloud Duty",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    },
    {
      "email": "john.smith@foo.bar",
      "displayName": "John Smith",
      "shiftName": "L2 Duty",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    },
    {
      "email": "tyrion.lannister@got.com",
      "displayName": "Tyrion Lannister",
      "shiftName": "L3 Duty",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    },
    {
      "email": "freddie.mercury@queen.uk",
      "displayName": "Freddie Mercury",
      "shiftName": "MGR Duty",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    }
  ]
}
```

# How to use it?

1. Install the Serverless Framework: https://serverless.com/
2. Configure your account and create at least one profile on your dashboard: https://dashboard.serverless.com/
3. Clone this repository
4. Uncomment this line in `serverless.yml` and replace `<YOUR_ORG>` with your Serverless Org:
   ```json
   # org: <YOUR_ORG>
   ```
5. Open a terminal on your local project directory:
`
$ sls deploy [--stage dev] [--region eu-west-1]
`

If you don't specify the `stage` and/or the `region`, il will use the values in the `custom` part of the `serverless.yml`:
 ```json
 custom:
    defaultRegion: eu-west-3
    defaultStage: dev
 ```

## Notifications

If you want to be notified when something went wrong:
1. Go to the AWS Console: https://aws.amazon.com/fr/console/
2. Go to SNS service
3. Add a subscription (by email for example) to the topic named `aws-microsoft-shifts-explorer-notifier-<stage>`
