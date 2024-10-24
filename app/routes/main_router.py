from flask import jsonify, render_template, redirect, url_for, flash, request, session

from app.services.openai_service import OpenAIService


def configure_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/message", methods=['POST'])
    def send_message():
        data = request.json
        message_body = data.get('message', 'Este es un mensaje simulado desde Twilio')
        from_number = data.get('from_number', '+14155551234')

        response = OpenAIService().handle_request(message_body, from_number)
        
        return jsonify({"status": "success", "response": response})
        