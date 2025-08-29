from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# 添加根路径路由 - 用于健康检查和验证部署
@app.route('/')
def home():
    return jsonify({
        'message': 'Flask API is running successfully on Vercel!',
        'status': 'active',
        'available_endpoints': {
            'POST /api/chat': 'Main chat endpoint for AI tutoring'
        },
        'documentation': 'This API is part of a PhD research project on culturally adaptive AI tutors.'
    })

# 原有的 /api/chat 路由保持不变
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # 检查 API 密钥是否存在
        if not DEEPSEEK_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
            
        data = request.get_json()
        
        # 验证请求数据
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
            
        user_message = data['message']
        mode = data.get('mode', 'standard')

        # 构建不同的系统提示词
        if mode == 'debias':
            system_message = """You are an impartial and knowledgeable AI tutor with a deep understanding of cultural diversity. When explaining concepts, you actively consider and integrate multiple perspectives, such as Eastern and Western viewpoints, avoiding assumptions or examples that carry cultural bias. Your goal is to make students from all cultural backgrounds feel included and understood."""
        else:
            system_message = "You are a helpful AI tutor."

        # 准备请求头和数据
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7
        }

        # 调用 DeepSeek API
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        
        # 记录响应状态和信息（会在Vercel日志中显示）
        print(f"DeepSeek API Status Code: {response.status_code}")
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content']
        
        return jsonify({'response': ai_response})

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        return jsonify({'error': f'AI service error: {err}'}), 500
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")
        return jsonify({'error': 'Failed to connect to the AI service'}), 500
    except KeyError as err:
        print(f"KeyError: {err}, Response: {response.text if 'response' in locals() else 'No response'}")
        return jsonify({'error': 'Unexpected response format from AI service'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Vercel 需要导出 app 实例
app = app

# 本地开发
if __name__ == '__main__':
    app.run(debug=True, port=5001)