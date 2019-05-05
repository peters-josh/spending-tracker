# Spending Tracker

Some assembly required.

This application is a simple spending tracker/budgeting service that can be used to monitor your finances across any payment mechanism (credit card, debit card, cash sharing app), that has purchase notifications via email. Please see the [associated blog post](https://medium.com/@jcpeters/how-i-got-control-of-my-spending-with-a-couple-no-code-services-and-only-100-lines-of-python-code-36c8ac75f670) for the inspiration behind the application.

The basic flow for the application is as follows: purchase notifications via email are auto forwarded to a [Zapier](https://zapier.com) service. Zapier sends the email subject and body via a HTTP `POST` request to the Python Flask API endpoint. The API parses the transaction information (description/amount) from the email body, assigns it a category, and writes the transaction to a Google Sheets workbook. All expenses across any payment mechanism can be viewed on the Sheets workbook, along with monthly summaries.

These instructions will walk you through how to set up the application for yourself and host it on Heroku. Fork and clone this repo to get started.


## Setup Email Purchase Notification
The secret API for all your financial accounts is purchase notifications. For each associated payment product, you need to turn on purchase notifications via email for any transaction you make.  For example, [Chase](https://www.chase.com/personal/credit-cards/login-update-account) gives instructions on their website, and Venmo has the option under your profile in the mobile app. 

## Google Sheets Integration

### Setup Workbook
Copy the following [workbook](https://docs.google.com/spreadsheets/d/1o6o5-q1O2rX9Ikv6kUx4_Gr1T0PAmeFwk4DYnu7NoKE/edit?usp=sharing) into your own Google drive. `File` > `Make a copy`. Make sure the copy is named `Budget`. There are instructions inside the workbook on how to use it.

### Google Sheets API
Head to the [Google API Console](https://console.developers.google.com). You should see a box that says "To view this page, select a project." Click the `create` button the right side. Give it a name and save. Click the `Credentials` tab on the left side. Select `Create credentials` > `Service account key`.

Select `New service account` from the drop down. Give the service account a name, for the role enter `Project` > `Editor`. Keep `JSON` selected and create it. The credentials file will be automatically downloaded.  Rename this file `credentials.json` and move it to the this application's directory.

Next, select `Manage service accounts`. Copy the email address of the service account you just created. Head back to the Sheets workbook you copied and share the document with the service account email. Make sure to give it access to edit.

Go to the [Google Sheets API](https://console.developers.google.com/apis/api/sheets.googleapis.com/overview) and enable it for your project.

## Deploy to Heroku 
Create a free account on [Heroku](http://heroku.com/) if you don't already have one. [Download the Heroku CLI](https://devcenter.heroku.com/articles/getting-started-with-python#set-up).

Inside the application folder run 

```
heroku create my-app-name-here-api-heroku
```
`my-app-name-here` is the unique name of the application, change it to what ever you want. Heroku will assign a unique name for you if you don't put anything.

The output of the command should look like the following:

```
Creating ⬢ my-app-name-here-api-heroku... done
https://my-app-name-here-api-heroku.herokuapp.com/ | https://git.heroku.com/my-app-name-here-api-heroku.git
```

Take note of the base URL for the application as well as the Heroku git repo it creates for you. 

By default, Heroku deploys what ever is on the origin master branch in your fork to Heroku. However, we don't want to upload the `credentials.json` file to Github since that contains your Google account info. To fix this, we can create a local branch that contains `credentials.json` while your master does not. 

Create a new branch.

```
git checkout -b "secret-branch"
```

Now add and commit the `credentials.json` file.

```
git add credentials.json
git commit -m "Added credentials file"
```

Deploy by pulling any upstream changes from the master branch and then pushing to Heroku, Then check out the master branch again.

```
git pull origin master
git push heroku secret-branch:master
git checkout master
```

Check the Heroku logs to make sure your build succeeded.

```
heroku logs
```

## Configure Email auto-forwarding & Zapier

### Set Up Zapier
Login or create an account on [Zapier](https://zapier.com). Create a new zap. Set the "Trigger App" as email. Save and continue.  Set anything you want for your email address prefix. Copy this email, click `Continue`, and then head over to your email client, i.e. Gmail.

Send an email to your new email address with something in the subject and body. Head back to Zapier and once it receives your email, click `Pull in sample` and then `Continue`.  

Now, we need to add an action to the Zap. Click the `Add a Step` button on the left side of the screen. Select `Action/Search`, search for `Webhooks`, and then select `POST`. 

Enter your Heroku URL + `/budget/api/email` at the end and change the Payload type to `Json`. Use the following key-value pairs for the Data section.

```
body: Body Plain
subject: Subject
```

Make sure you are click the `+` button on the key entry and select `Body Plain` and `Subject`. You should see the text you entered for the body and subject in the test email you sent.

Continue to the next step, send a test, and then finish. Turn the Zap on.

### Auto-Forward emails to Zapier
Auto forward all of your purchase notifications to your new Zapier email address. For Gmail, instructions for setting up auto-forwarding with filtering for your specific messages can be found [here](https://support.google.com/mail/answer/10957?hl=en). 

When auto forwarding with Gmail, you'll need to follow [these](https://zapier.com/help/autoforwarding-email-gmail/) instructions to verify your email address as you cant view the Zapier inbox.

## Parsing Purchase notifications
By default, the application is set up to parse Chase credit card purchase notifications and Venmo charge & payment notifications. If you want more/different integrations, you'll have to set them up yourself. The parsing of the purchase notifications is done via regex. 

The body of each request is set to print in the Heroku logs with `print(repr(body))`.  When an incoming purchase notification sent to the API, use the `Heroku logs` to view the logs and copy the raw email body, and then create a regex to parse the description and amount.  A helpful tool for building your regex expressions is [here](https://regex101.com/). I used a positive lookahead and a positive lookbehind to parse the result. Add a new `elif` block in the `parse_email()` function to capture this transaction type.


## Adding New Categories 
Each transaction is assigned a category based on the description that is parses from the email. Add the common places you buy things from the in the `constants.py`. Be sure to redeploy to Heroku once you make changes.

## Conclusion
Once set up this, this application offers a simple, unified view of your transaction history across all your payment methods. The only maintenance needed is if your credit card company decides to change the format of their purchase notification emails.  You'll have to update your regex, but this should be very infrequent.  

Because the app uses a Google Sheets workbook as the frontend and backend, it is customizable and open for you to do your own spending analysis.
