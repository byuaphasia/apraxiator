# Apraxiator
Server implemented in python for speech pathology tests. Designed to work with the [Project Apraxia](https://github.com/RyanRemer/project_apraxia) app as an optional back-end. Focuses on Word Syllable Duration (WSD) calculations. Running "run.sh" will install the necessary dependencies and run the server on a linux machine. Runs on port 8080.

## Environment Variables
This uses the following environment variables to manage its state and access credentials:

| Variable Name      | Values                                   | Default    | Explanation     |
|--------------------|------------------------------------------|------------|-----------------|
| APX_ENV            | local, server, etc.                      | local      | Determines which config file to use (explained in the next section)                                                                                                                  |
| APX_AWS_SES_REGION | us-west-2                                | us-west-2  | The region that the SES service is hosted in                                                                                                                                         |
| APX_AWS_S3_REGION  | us-west-2                                | us-west-2  | The region that the S3 service is hosted in                                                                                                                                          |
| APX_AWS_ACCESS     | ADVKALE7LAAEVNALEI34                     |            | The AWS Access Key generated for an IAM role                                                                                                                                         |
| APX_AWS_SECRET     | HWErGUkkcq42fmlRtY9UveXmPTRnWmo65D/PLEGr |            | The AWS Secret Key generated for an IAM role                                                                                                                                         |
| APX_MYSQL_HOST     | localhost, mydb.asdf.us.rds.amazonaws.com| localhost  | The host name of the MySQL service connection                                                                                                                                        |
| APX_MYSQL_USER     | root, server                             |            | The user name to connect to the MySWL service                                                                                                                                        |
| APX_MYSQL_PASSWORD | Password1                                |            | The password to connect to the MySWL service                                                                                                                                         |
| APX_TEST_MODE      | isolated, connected                      | isolated   | Determines whether to run the unit tests in an isolated environment (no MySQL or S3 access) or connected environment (test MySQL and S3 connection)                                  |

## Configuration Files
A json configuration file can be defined in the `src/config/` folder. By default, the `local.json` file will be used. The `APX_ENV` environment variable determines which config file will be loaded. For example, `APX_ENV` set to `local` will load the `local.json` config file, while setting `APX_ENV` to `custom` will load the `custom.json` config file that has been previously created. The `server.json` file is shown here as an example of the config file format.
```json
{
  "name": "server",
  "dbName": "apraxiator",
  "s3Bucket": "appraxia",
  "jwkFile": "../apx-resources/auth/jwk.json",
  "templatesDir": "src/utils/pdfgenerator/templates/",
  "emailSender": "Tyson Harmon <projectapraxia@gmail.com>"
}
```

## API Endpoints
For each endpoint, a Cognito signed JWT token is expected to identify the user. This should be passed in the request headers under the "TOKEN" key.

### GET /healthcheck
A healthcheck endpoint to test whether the server is up and running. DOES NOT REQUIRE JWT TOKEN IN HEADER. Returns a json response in this form:
```json
{
  "message": "all is well"
}
```


### POST /evaluation
Creates a new evaluation. This expects a json body in this form:
```json
{
  "age": "50",
  "gender": "male",
  "impression": "apraxia,aphasia"
}
```
The age is expected to be a string version of the age or "no answer". The impression is expected to be a comma delimited list of impressions. This will return a json response in this form:
```json
{ 
  "evaluationId": "EV-1234"
}
```

### POST /evaluation/\<evaluationId>/ambiance
Attaches an ambiance to an evaluation. Extracts a threshold from the ambiance recording and adds that to the evaluation object. This expects a wav file representing a recording of the ambient environment to be present in the request body. This should be formatted as a multipart form with the key set to "recording" for the ambiance file. Returns an empty json object if successful.

### GET /evaluation
Returns all evaluations tied to the implicitly provided user. Returns a json response in this form:
```json
{
  "evaluations":[
    {
      "evaluationId": "EV-1234",
      "age": "50",
      "gender": "male", 
      "impression": "apraxia,aphasia",
      "dateCreated": "25/12/2042"
    }
  ]
}
```

### GET /evaluation/\<evaluationId>/attempts
Returns all attempts tied to the provided evaluationId. This will return a json response in this form:
```json
{
  "attempts":[
    {
      "attemptId": "AT-1234",
      "evaluationId": "EV-1234",
      "word": "gingerbread",
      "wsd": 256.79,
      "duration": 770.37,
      "active": true,
      "dateCreated": "25/12/2042"
    }
  ]
}
```
  
### POST /evaluation/\<evaluationId>/attempt?syllableCount=3&word=gingerbread
Creates a new attempt tied to the provided evaluation. Requires that the syllableCount and word are set in the query parameters or multipart form body. An optional parameter "method" allows selection between the different approaches to calculating WSD. Available options are "filterer", "endpoint", "vad", or "average". Another optional parameter defines whether the attached recording will be saved in connection with the attempt. Unless the parameter "save" is set to false, the default will be to save the recording. Like /evaluation, a wav file should be in the multipart request body under the key "recording" which represents the repitition attempt. Returns a json response in this form:
```json
{
  "attemptId": "AT-1234",
  "wsd": 256.79
}
```

### PUT /evaluation/\<evaluationId>/attempt/\<attemptId>
Allows for changing the "active" status of an attempt. Expects "active" to be set to true or false in the params, form, or json body. Returns empty json object.
  
### POST /evaluation/\<evaluationId>/attempt/\<attemptId>/recording
Saves a recording and ties it to the specified evaluation and attempt. Expects a wav file in the multipart request body under the key "recording". Returns empty json object.
  
### GET /evaluation/\<evaluationId>/attempt/\<attemptId>/recording
Returns the saved recording tied to the specified evaluation and attempt. Streams the response in the body.

### POST /evaluation/<evaluation_id>/report
Generates an evaluation report and sends it to the provided email. Returns an empty json object if successful. Expects a json body in this form:
```json
{
  "email": "email@email.com",
  "name": "John Smith"
}
```

Returns an unnecessary json response in this form:
```json
{
    "attempts": [
        {
            "word": "gingerbread",
            "syllables": 3,
            "wsd": 123.456789,
            "wsd_str": "123.45"
        }
    ],
    "evaluation": {
        "evaluationId": "EV.......",
        "age": "50",
        "gender": "Male",
        "impression": "impression",
        "dateCreated": "January 01, 2020"
    }
}
```

### POST /waiver/subject
Saves a subject waiver and emails it to the client and clinician. Returns an empty json object if successful.

* Expects a .png file representing the signature in the request body with the key set to "subjectSignature".
* Expects a json body in this form:
```json
{
  "subjectName": "John Smith",
  "subjectEmail": "email@example.com",
  "dateSigned": "January 01, 2020",
  "clinicianEmail": "email@example.com"
}
```

### POST /waiver/representative
Saves a representative waiver and emails it to the client and clinician. Returns an empty json object if successful.

* Expects a .png file representing the signature in the request body with the key set to "representativeSignature".
* Expects a json body in this form:
```json
{
  "subjectName": "John Smith",
  "subjectEmail": "email@example.com",
  "representativeName": "Jane Smith",
  "relationship": "Mother",
  "dateSigned": "January 01, 2010",
  "clinicianEmail": "email@example.com"
}
```

### GET /waiver
Returns the waiver tied to the provided subject email (subjectEmail), subject name (subjectName), and owner (provided by jwt token in headers). Provide subjectEmail and subjectName in the query parameters (after a question mark in the URL). This will return a json response in this form:
```json
{
  "subjectName": "John Smith",
  "subjectEmail": "email@example.com",
  "date": "January 01, 2020",
  "waiverId": "WV-1234"
}
```

### PUT /waiver/\<waiver_id>/invalidate
Allows for changing the "valid" status of the waiver corresponding to the waiver_id. Returns empty json object.

### POST /export
Allows for admin users to export data. Expects a json body in this form:
```json
{
  "startDate": "2014-12-25",
  "endDate": "2015-01-01",
  "includeRecordings": true
}
```
Date parameters must be in the form YYYY-MM-DD. The `includeRecordings` value determines whether the endpoint returns a csv or zip file. It defaults to `true`.

### GET /user
Returns a json body with the user type based on the JWT-authenticated user ID. Possible values are `admin` and `user`. This is returned in a json body of this form:
```json
{
  "userType": "admin"
}
```
