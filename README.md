# Apraxiator
Server implemented in python for speech pathology tests. Designed to work with the [Project Apraxia](https://github.com/RyanRemer/project_apraxia) app as an optional back-end. Focuses on Word Syllable Duration (WSD) calculations. Running "run.sh" will install the necessary dependencies and run the server on a linux machine. Runs on port 8080. A healtcheck endpoint is available for testing at /healtcheck.


## API Endpoints
For each endpoint, a cognito signed JWT token is expected to identify the user. This should be passed in the request headers under the "TOKEN" key.

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

### POST /sendReport/\<evaluation_id\>
Generates an evaluation report and sends it to the provided email. Returns an empty json object if successful. Expects a json body in this form:
```json
{
  "email": "email@email.com",
  "name": "John Smith"
}
```