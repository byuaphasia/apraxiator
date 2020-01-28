# Apraxiator
Server implemented in python for speech pathology tests. Designed to work with the [Project Apraxia](https://github.com/RyanRemer/project_apraxia) app as an optional back-end. Focuses on Word Syllable Duration (WSD) calculations. Running "run.sh" will install the necessary dependencies and run the server on a linux machine. Runs on port 8080. A healtcheck endpoint is available for testing at /healtcheck.


## API Endpoints
For each endpoint, a cognito signed JWT token is expected to identify the user. This should be passed in the request headers under the "TOKEN" key.

### POST /evaluation
Creates a new evaluation. This expects a wav file representing a recording of the ambient environment to be present in the request body. This should be formatted as a multipart form with the key set to "recording". This will return a json response in the form:
```json
{ 
  "evaluationId": "EV-1234"
}
```

### GET /evaluation/\<evaluationId>
Returns all attempts tied to the provided evaluationId. This will return a json response in the form:
```json
[
  {
    "attemptId": "AT-1234",
    "evaluationId": "EV-1234",
    "word": "gingerbread",
    "wsd": 256.79,
    "duration": 770.37,
    "dateCreated": "25/12/2042"
  }
]
```
  
### POST /evaluation/\<evaluationId>/attempt?syllableCount=3&word=gingerbread
Creates a new attempt tied to the provided evaluation. Requires that the syllableCount and word are set in the query parameters. An optional parameter "method" allows selection between the different approaches to calculating WSD. Available options are "filterer", "endpoint", or "average". Like /evaluation, a wav file should be in the multipart request body under the key "recording" which represents the repitition attempt.
  
### POST /evaluation/\<evaluationId>/attempt/\<attemptId>/recording
Saves a recording and ties it to the specified evaluation and attempt. Expects a wav file in the multipart request body under the key "recording".
  
### GET /evaluation/\<evaluationId>/attempt/\<attemptId>/recording
Returns the saved recording tied to the specified evaluation and attempt. Streams the response in the body.
