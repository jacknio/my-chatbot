from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# ========== 阿里云 EAS 配置 ==========
# 根据你提供的公网调用地址，若你的模型是基于 Chat-LLM-Webui 部署，则一般调用接口为 /v1/chat/completions
EAS_ENDPOINT = "http://zhongshiqiao.1350319374447404.cn-shanghai.pai-eas.aliyuncs.com/v1/chat/completions"
# Token（直接使用，不加Bearer前缀）
EAS_TOKEN = "YWI1MmJkYzUwZGY3NzJiYzM1MWIwMWYwMjI3MWEwZmM1MTA5NjA5Mg=="
# =========================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_ai():
    try:
        # 获取前端提交的数据
        data = request.get_json()
        user_input = data.get('question', '').strip()
        if not user_input:
            return jsonify({"error": "问题不能为空"}), 400

        # 构造请求体：采用 OpenAI 兼容格式（可根据实际需求调整）
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.6,
            "max_tokens": 300,
            "stream": False
        }

        # 调用阿里云 EAS 服务
        response = requests.post(
            EAS_ENDPOINT,
            headers={
                "Authorization": EAS_TOKEN,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            # 假设返回格式为：{"choices": [{"message": {"content": "回答内容"}}]}
            return jsonify({
                "answer": result['choices'][0]['message']['content']
            })
        else:
            return jsonify({
                "error": f"API 返回错误（状态码 {response.status_code}）",
                "detail": response.text
            }), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"网络请求失败: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

if __name__ == '__main__':
    # 这里使用端口5001，如有需要可修改
    app.run(host='0.0.0.0', port=5001, debug=False)
