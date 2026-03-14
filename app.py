# Made by rohitt!!!

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def convert(s):
    """Convert seconds to human readable format"""
    d, h = divmod(s, 86400)
    h, m = divmod(h, 3600)
    m, s = divmod(m, 60)
    return f"{d} Day {h} Hour {m} Min {s} Sec"

def get_bind_info(access_token):
    """Get bind information from Garena API"""
    url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
    payload = {'app_id': "100067", 'access_token': access_token}
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }

    try:
        response = requests.get(url, params=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()

            email = data.get("email", "")
            email_to_be = data.get("email_to_be", "")
            countdown = data.get("request_exec_countdown", 0)

            # UI friendly values
            current_email = email if email else "Not set"
            pending_email = email_to_be if email_to_be else "None"

            result = {
                "status": "success",
                "status_code": 200,
                "data": {
                    "current_email": current_email,
                    "pending_email": pending_email,
                    "countdown_seconds": countdown,
                    "countdown_human": convert(countdown) if countdown > 0 else "0",
                    "raw_response": data
                },
                "summary": ""
            }

            # Summary logic (UI friendly)
            if email == "" and email_to_be != "":
                result["summary"] = f"Pending email confirmation: {email_to_be} - Confirms in: {convert(countdown)}"

            elif email != "" and email_to_be == "":
                result["summary"] = f"Email confirmed: {email}"

            elif email == "" and email_to_be == "":
                result["summary"] = "No recovery email set"

            return result

        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": f"API returned status code: {response.status_code}",
                "response_text": response.text[:500] if response.text else "No response body"
            }

    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Request timeout (30 seconds)"}

    except requests.exceptions.ConnectionError:
        return {"status": "error", "error": "Connection error - cannot reach Garena API"}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": f"Request exception: {str(e)}"}

    except Exception as e:
        return {"status": "error", "error": f"Unexpected error: {str(e)}"}


@app.route('/bind_info', methods=['GET'])
def bind_info_endpoint():
    access_token = request.args.get('access_token')

    if not access_token:
        return jsonify({
            "status": "error",
            "error": "access_token parameter is required"
        }), 400

    result = get_bind_info(access_token)

    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Garena Bind Info API",
        "version": "1.0"
    }), 200


@app.route('/')
def home():
    return jsonify({
        "message": "Garena Bind Info API running",
        "endpoint": "/bind_info?access_token=TOKEN"
    })


if __name__ == "__main__":
    app.run()