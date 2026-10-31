# Setup guide (AWS console)

This takes about 30 to 45 minutes the first time. Everything is done in the AWS console in your browser.

**Before you start:** make an AWS account, then set a budget alert (Billing -> Budgets) so you never get a surprise bill. Check AWS's current free-tier rules. When you finish, delete what you created (last step).

Use one region the whole time (for example Mumbai, `ap-south-1`).

## Step 1: Create the DynamoDB table

1. Open **DynamoDB** -> **Create table**.
2. Table name: `registrations`.
3. Partition key: `id`, type **String**.
4. Leave the other settings as they are and click **Create table**.

## Step 2: Create the Lambda function

1. Open **Lambda** -> **Create function** -> **Author from scratch**.
2. Name: `registrationHandler`. Runtime: the latest **Python 3.x** shown.
3. Click **Create function**.
4. In the code editor, replace everything with the code from `lambda/lambda_function.py`, then click **Deploy**.
5. Go to **Configuration -> Environment variables -> Edit** and add:
   - Key: `TABLE_NAME`
   - Value: `registrations`

## Step 3: Let Lambda use the table (IAM)

1. In Lambda, open **Configuration -> Permissions** and click the **role name**. This opens IAM.
2. Click **Add permissions -> Create inline policy -> JSON** and paste this (replace the table ARN with yours; you can copy it from the DynamoDB table's page):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:Scan"],
      "Resource": "PASTE_YOUR_TABLE_ARN_HERE"
    }
  ]
}
```

3. Name it `registrations-access` and save. Lambda can now save and read, and nothing else.

## Step 4: Create the API

1. Open **API Gateway** -> **Create API** -> **HTTP API** -> **Build**.
2. Add an integration: **Lambda**, and choose `registrationHandler`. Name the API `registration-api`.
3. Add two routes, both pointing to that Lambda:
   - `GET /registrations`
   - `POST /registrations`
4. Keep the default stage with auto-deploy on, then create the API.
5. Open **CORS** in the left menu and set:
   - Allow origin: `*`
   - Allow methods: `GET, POST, OPTIONS`
   - Allow headers: `content-type`
6. Copy the **Invoke URL** from the API's page. It looks like `https://abc123.execute-api.ap-south-1.amazonaws.com`.

## Step 5: Connect the page

1. Open `frontend/index.html` and replace `YOUR_API_URL` with the invoke URL (no slash at the end).
2. Double-click the file to open it in your browser.
3. Register yourself. The name should show up in the list.
4. Check DynamoDB -> **Explore table items** to see the saved record.

## Step 6 (optional): Put the page online

In **AWS Amplify**, choose **Host a web app**, pick manual deployment (drag and drop), and upload a zip of the `frontend` folder. You get a public link.

## If something goes wrong

- **"Could not reach the server" / CORS error:** recheck Step 4 part 5 and the URL in `index.html`.
- **500 error:** open Lambda -> **Monitor -> View CloudWatch logs**. Usually `TABLE_NAME` is wrong or the IAM policy is missing.
- **404 error:** the route is missing. Check that both routes exist and the URL has no extra slash.

## Take screenshots

Save these in `docs/screenshots/`: the working form, a record in the DynamoDB table, and the API routes page. Then remove the comment markers around the images in the README.

## Clean up when you're done

Delete the API, the Lambda function, the DynamoDB table and the Amplify app so nothing keeps running.
