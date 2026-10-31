# ServerLess-WebPage-Using-API-gateway-and-DynamoDB---Cloud-Computing
# Serverless Registration Form

A simple registration web page that runs on AWS **without a server of my own**. A person fills in their name and email, the details are saved in a database, and the page shows everyone who has registered so far.

I first built this with my team for our Cloud Computing Lab (2023-24, B.Tech IT, Sree Vidyanikethan Engineering College). I don't have the original files anymore, so I rebuilt it from our lab report and deployed it again myself for this repo.

## What this project is about

Normally, a web app needs a server that is always switched on, even when nobody is using it. Someone has to set it up, update it and pay for it all day.

In a **serverless** setup, I only write the code and AWS runs it when a request comes in. When nobody is using the page, nothing is running. If many people use it at once, AWS handles the extra load by itself.

This project is a small, real example of that idea: a registration form built from managed AWS services instead of a server.

## What it can do

- Take a registration (name, email and an optional roll number) from a web form
- Check the input before saving (name can't be empty, email must look valid)
- Save each registration in a DynamoDB table with a unique ID and a timestamp
- Show the list of registered people on the same page, newest first
- Show clear messages when something goes wrong, instead of failing silently

## How it works

```
Browser (HTML + JavaScript)
        |
        v
Amazon API Gateway   <- the public URL that receives requests
        |
        v
AWS Lambda (Python)  <- my code: checks input, saves or reads data
        |
        v
Amazon DynamoDB      <- the table that stores the registrations

(AWS IAM decides what Lambda is allowed to do. CloudWatch keeps its logs.)
```

**When someone registers:**
1. They fill in the form and click Register.
2. JavaScript on the page sends the details to the API Gateway URL as a `POST` request.
3. API Gateway hands the request to the Lambda function.
4. Lambda checks the details, creates an item with a unique ID and the current time, and saves it in DynamoDB.
5. Lambda sends back a message, and the page shows "Thanks for registering!" and reloads the list.

**When the page loads:**
1. The page sends a `GET` request to the same API.
2. Lambda reads the saved items from DynamoDB, sorts them with the newest first, and returns them.
3. The page shows them as a list.

## Tech used

| Part | What I used | What it does here |
|---|---|---|
| Front end | HTML, CSS, JavaScript | The form and the list, no frameworks |
| API | Amazon API Gateway (HTTP API) | Gives the app a public URL and sends requests to Lambda |
| Back end | AWS Lambda, Python, boto3 | Runs my code only when a request arrives |
| Database | Amazon DynamoDB | Stores the registrations |
| Permissions | AWS IAM | Lets Lambda use only this one table |
| Logs | Amazon CloudWatch | Helps me find out why something failed |
| Hosting (optional) | AWS Amplify | Puts the page online with a public link |

## The API

Base URL: the invoke URL that API Gateway gives you.

**`POST /registrations`** saves a new registration.

Request body:
```json
{ "name": "Anjali Rao", "email": "anjali@example.com", "rollNo": "21121A1234" }
```
Success reply (`201`): `{ "message": "Registered!", "id": "<unique id>" }`
Error replies: `400` for missing or invalid input, `500` if saving fails.

**`GET /registrations`** returns up to 50 saved registrations, newest first (`200`).

## What gets stored

Each registration is one item in the `registrations` table:

| Field | Meaning |
|---|---|
| `id` | Unique ID created by Lambda (this is the table's key) |
| `name` | Name of the person |
| `email` | Email of the person |
| `rollNo` | Optional roll number |
| `createdAt` | Date and time of registration (UTC) |

## Project structure

```
frontend/index.html          the form and the list of registrations
lambda/lambda_function.py    the Lambda code (POST saves, GET lists)
docs/setup-guide.md          step-by-step AWS setup for beginners
docs/screenshots/            screenshots of the page
```

## Run it yourself

The full steps are in [docs/setup-guide.md](docs/setup-guide.md). In short:

1. Create a DynamoDB table called `registrations` with the key `id` (String).
2. Create a Lambda function, paste in `lambda/lambda_function.py`, and set the environment variable `TABLE_NAME=registrations`.
3. Give the Lambda role permission to use only that table (`PutItem` and `Scan`).
4. Create an HTTP API in API Gateway with the routes `GET /registrations` and `POST /registrations`, and turn on CORS.
5. Paste the API URL into `frontend/index.html` and open the file in a browser.

## Things I was careful about

- **Least permission:** the Lambda role can only save to and read from this one table, nothing else in the account.
- **Input checks:** Lambda checks every request on the server side, not just in the browser, because anyone can call an API directly.
- **Safe display:** the page adds names to the list as plain text, so someone can't sneak HTML or scripts in through the name field.
- **No secrets in the code:** the table name comes from an environment variable, and `.gitignore` blocks keys and passwords from being uploaded.

## Limitations

This is a learning project, so it has some limits I know about:

- **The list is public.** Anyone with the page can see the names and emails, so only use fake or non-sensitive details when testing. A real app would need a login (for example AWS Cognito) and would not show emails to everyone.
- **CORS is open (`*`)** so the page works from anywhere while testing. A real app would allow only its own website.
- **No duplicate check.** The same email can register more than once.
- **The list shows only 50 entries** and has no search or paging.
- **No edit or delete.** It only creates and reads.

## Ideas to improve it

- Block duplicate emails
- Add login so only the admin can see the list
- Add delete and edit
- Set up the whole thing with AWS SAM or CloudFormation so it can be created with one command
- Add automated tests for the Lambda function

## What I learned

- A serverless app is a few small pieces that each do one job. API Gateway is the front door, Lambda runs the code, and DynamoDB keeps the data.
- A Lambda function can only touch other AWS services if its IAM role allows it, so permissions need to be set deliberately.
- Browsers block calls to a different domain unless CORS is turned on. I ran into this error first and fixed it in API Gateway.
- CloudWatch logs are the quickest way to find out why a Lambda call failed.
- Checking input on the server matters, even when the form already checks it.

