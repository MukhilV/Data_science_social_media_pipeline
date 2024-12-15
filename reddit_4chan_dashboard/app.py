from flask import Flask, render_template, jsonify
from app import create_app

app = create_app()

@app.route('/')
def home():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

