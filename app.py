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
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    
    # ########### 新增调试代码 ###########
    print(f"DeepSeek API Status Code: {response.status_code}")
    print(f"DeepSeek API Response Text: {response.text}")
    # ################################
    
    response.raise_for_status()  # 如果状态码不是200，会抛出异常
    response_data = response.json()
    ai_response = response_data['choices'][0]['message']['content']
    return jsonify({'response': ai_response})

except requests.exceptions.HTTPError as err:
    # 专门处理HTTP错误（如401认证失败，429超过速率限制）
    print(f"HTTP Error occurred: {err}")
    return jsonify({'error': f'AI service error: {err}'}), 500
except requests.exceptions.RequestException as err:
    # 处理其他请求相关的错误（如网络问题）
    print(f"Request Error: {err}")
    return jsonify({'error': 'Failed to connect to the AI service'}), 500
except KeyError as err:
    # 处理JSON解析后找不到Key的错误
    print(f"KeyError: Could not find key {err} in the response: {response_data}")
    return jsonify({'error': 'Unexpected response format from AI service'}), 500
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    # 选择一个其他端口，例如 5001, 8000, 8080 等
    app.run(debug=True, port=5001)