from flask import Flask, request, jsonify
from flask_cors import CORS  # 处理跨域请求
import requests  # 用于调用 DeepSeek API
import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

app = Flask(__name__)
CORS(app)  # 允许前端请求

# DeepSeek API 的端点
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    mode = data.get('mode', 'standard')

    # 构建不同的系统提示词来模拟“标准”和“去偏见”模式
    if mode == 'debias':
        system_message = """You are an impartial and knowledgeable AI tutor with a deep understanding of cultural diversity. When explaining concepts, you actively consider and integrate multiple perspectives, such as Eastern and Western viewpoints, avoiding assumptions or examples that carry cultural bias. Your goal is to make students from all cultural backgrounds feel included and understood."""
    else:
        system_message = "You are a helpful AI tutor." # 标准模式

    # 准备请求头和数据，用于调用 DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",  # 指定使用的模型
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        # 向 DeepSeek API 发送请求
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response_data = response.json()

        # 从 DeepSeek 的响应中提取回复内容
        ai_response = response_data['choices'][0]['message']['content']
        return jsonify({'response': ai_response})

    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return jsonify({'error': 'Failed to get response from AI'}), 500

if __name__ == '__main__':
    # 选择一个其他端口，例如 5001, 8000, 8080 等
    app.run(debug=True, port=5001)