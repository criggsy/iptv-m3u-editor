from flask import Flask, render_template, request
import json


app = Flask(__name__)


with open('output.json', 'r') as f:
    data = json.load(f)

# Define your app routes here
@app.route("/")
def home():
    with open("output.json", "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        data = {} # or handle the error appropriately
    return render_template("home.html", data=data)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # Extract the updated data from the form
        updated_data = request.form["data"]

        # Update the data dictionary with the updated data
        # (You may want to add some error handling here)
        data.clear()
        data.update(updated_data)

        # Save the updated data to a file
        with open("output.json", "w") as f:
            f.write(updated_data)

        return "Data saved successfully!"
    else:
        return render_template("edit.html", data=data)

if __name__ == '__main__':
    app.debug = True
    app.run()