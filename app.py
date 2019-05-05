import re
from flask import Flask, jsonify, request
from sheets import Sheets
import constants

app = Flask(__name__)


@app.route("/budget/api/email", methods=["POST"])
def parse_email():
    payload = request.json
    body = payload["body"]
    subject = payload["subject"]
    sheet = Sheets()
    print(repr(body))

    if "You paid" in subject:
        description = extract("(?<=\) \\n \\n)(.*)(?= \\n \ T)", body)
        amount = extract("(?<=\- \$)(.*)(?= \\n     \\n  L)", body)
        category = assign_cat_venmo(description)
        method = "Vemno"
        sheet.add_expense(amount, description, category, method)

    elif "charge request" in subject:
        description = extract("(?<=\-5\) \\n \\n)(.*)(?= \\n  T)", body)
        amount = extract("(?<=\- \$)(.*)(?= \\n     \\n  L)", body)
        category = assign_cat_venmo(description)
        method = "Vemno"
        sheet.add_expense(amount, description, category, method)

    elif "Your Single Transaction Alert from Chase" in subject:
        description = extract("(?<= at )(.*)(?= has been authorized)", body)
        amount = extract("(?<=charge\ of\ \(\$USD\) )(.*)(?=\ at)", body)
        category = assign_cat_card(description)
        method = "Chase"
        sheet.add_expense(amount, description, category, method)

    return jsonify({"success": "true"})


def extract(regex, body):
    result = re.search(regex, body)
    return "NOT FOUND" if result is None else result.group()


def assign_cat_venmo(description):
    for venmo in constants.VENMOS.keys():
        if venmo in description.lower():
            return constants.VENMOS[venmo]
    return "NOT FOUND"


def assign_cat_card(description):
    for store in constants.STORES.keys():
        if store in description.lower():
            return constants.STORES[store]
    return "NOT FOUND"


if __name__ == "__main__":
    app.run()
