from flask import Flask, request, jsonify, send_from_directory
import anthropic
import base64
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/identify', methods=['POST'])
def identify_coin():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    image_data = data['image']
    if ',' in image_data:
        image_data = image_data.split(',')[1]

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured on server'}), 500

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Please examine this coin image carefully. Identify:\n"
                                "1. The coin type/name (e.g., US Quarter, British Penny, etc.)\n"
                                "2. The country of origin\n"
                                "3. The year it was minted (look for the date on the coin)\n"
                                "4. Any notable details (mint mark, special edition, estimated condition/grade, approximate value)\n\n"
                                "If the image is unclear or not a coin, say so. "
                                "Format your response with clear labeled sections."
                            )
                        }
                    ],
                }
            ],
        )
        result = message.content[0].text
        return jsonify({'result': result})
    except anthropic.AuthenticationError:
        return jsonify({'error': 'Invalid API key'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
