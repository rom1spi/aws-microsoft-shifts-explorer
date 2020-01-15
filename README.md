# aws-microsoft-shifts-explorer (Beta)
 A tool to explore Microsoft Shifts data

It is still considered as a Beta version because we use some features of the Microsoft Graph API which are currently in Beta version. 

## Use case
Your organization uses Microsoft Teams, and employees' planing are stored in Microsoft Shifts.
You want to get all users contact information for all shifts filtered by:
- a given period
or
- the next given week day

## Architecture

This module is fully serverless.

![](res/AWS_Microsoft_Shifts_Explorer.png)

## Sample Request:

### /shiftsusers/period
```json
{
    "filters": {
        "sharedShiftPeriod": {
            "startDateTime": "2019-12-17T00:00:00.000Z",
            "endDateTime": "2019-12-18T00:00:00.000Z"
        },
        "shiftNameContains": ["duty", "show"]
    }
}
```

### /shiftsusers/weekday
```json
{
    "filters": {
        "nextWeekday": "TUE",
        "shiftNameContains": ["duty", "show"]
    }
}
```

Possible values for `nextWeekday`: 
`MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`, `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `SUN`

The `shiftNameContains` field contains a list of words which shift name must contain (at least one of them).
If you leave it empty (`"shiftNameContains": []`), all shifts will be returned.

## Sample Response:
```json
{
  "statusCode": 200,
  "body": [
    {
      "email": "romain.spinelli@foo.bar",
      "mobilePhone": "+33 0 12 34 56 78",
      "displayName": "Romain Spinelli",
      "shiftName": "Cloud Duty",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    },
    {
      "email": "john.smith@foo.bar",
      "mobilePhone": "+41 12 345 67 89",
      "displayName": "John Smith",
      "shiftName": "L2 Duty",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    },
    {
      "email": "tyrion.lannister@got.com",
      "mobilePhone": "+354 123 45 67",
      "displayName": "Tyrion Lannister",
      "shiftName": "TV show",
      "startDateTime": "2019-12-24T08:00:00Z",
      "endDateTime": "2019-12-24T17:00:00Z"
    },
    {
      "email": "freddie.mercury@queen.uk",
      "mobilePhone": "+44 12 34 56 7890",
      "displayName": "Freddie Mercury",
      "shiftName": "TV show",
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
$ npm install serverless-pseudo-parameters
$ sls deploy [--stage dev] [--region eu-west-1] --myApiKey `<YOUR_API_KEY_VALUE>`
`

The value you specified in `<YOUR_API_KEY_VALUE>` must then be used in the headers `x-api-key` of your API call.

In your terminal, your deployment might display something like:
![](res/deploy.png)

Besides you can see that the 2 endpoints are listed in the "Service Information" part.

If you don't specify the `stage` and/or the `region`, il will use the values in the `custom` part of the `serverless.yml`:
 ```json
 custom:
    defaultRegion: eu-west-3
    defaultStage: dev
 ```
## Credentials

You have to store your Microsoft account credentials in a secure way:
1. Connect to the AWS Console: https://aws.amazon.com/fr/console/
2. Select the region you want to deploy the service
3. Go to Secrets Manager service
4. Click on "Store new secret" button
5. Select "Other type of secrets"
6. Click on "Plaintext" tab
7. Copy/paste the following code block in the "plan text" tab, and replace the attributes' values between `<>`:
 
```json
{
  "USERNAME": "<username>",
  "PASSWORD": "<password>",
  "TENANT_ID": "<tenant_id>",
  "TEAM_ID": "<team_id>",
  "SECRET_KEY": "<secret_key>",
  "CLIENT_ID": "<client_id>"
}
```

If you don't know how to valorize these attributes, connect to the Azure portal to find your own attributes:
https://portal.azure.com/

**Important**: 
- The username must be like: `<username>@<yourdomain>.<ext>` (not just `username`)
- The user must belong to the team
- Advise: create a generic user in your Azure AD (without licence on Office products), and give it access to the tenant (TENANT_ID), and add it to the team (TEAM_ID)

8. Enter the Secret name: `Microsoft/Graph/API/ShiftsExplorer/<STAGE>`
 
 Replace `<STAGE>` with the value of your stage (used to deploy your application)
 Examples: 
  * `Microsoft/Graph/API/ShiftsExplorer/dev`
  * `Microsoft/Graph/API/ShiftsExplorer/test`
  * `Microsoft/Graph/API/ShiftsExplorer/prod`

## Notifications

If you want to be notified when something went wrong:
1. Go to the AWS Console: https://aws.amazon.com/fr/console/
2. Go to SNS service
3. Add a subscription (by email for example) to the topic named `aws-microsoft-shifts-explorer-notifier-<stage>`
