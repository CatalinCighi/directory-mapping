from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the directory path and selected format from the form input
        directory_path = request.form.get("directory")
        output_format = request.form.get("format")

        if directory_path and output_format:
            # Process the directory path and format here (e.g., list files, etc.)
            return f"Directory selected: {directory_path}<br>Format selected: {output_format}"
        return "No directory or format selected"
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
