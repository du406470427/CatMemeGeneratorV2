import re
import json
import requests

def get_script():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        google_api_key = config["google_api_key"]
    except FileNotFoundError:
        print("错误：未找到 config.json 配置文件")
        return
    except json.JSONDecodeError:
        print("错误：config.json 格式不正确")
        return
    except KeyError:
        print("错误：config.json 中缺少 google_api_key 字段")
        return

    user_theme = input("请输入视频主题/标题：").strip()
    
    try:
        # 读取提示词模板
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        # 检查占位符
        required_placeholders = ["[user input]", "[detail_json]"]
        missing = [ph for ph in required_placeholders if ph not in prompt_template]
        if missing:
            print(f"错误：未在 prompt.txt 中找到以下占位符: {', '.join(missing)}")
            return

        # 读取素材信息
        try:
            with open("memes/detail.json", "r", encoding="utf-8") as f:
                detail_content = f.read()
        except FileNotFoundError:
            print("错误：找不到 memes/detail.json 文件")
            return
        except Exception as e:
            print(f"读取 memes/detail.json 时发生错误: {str(e)}")
            return
            
        # 生成最终提示词
        final_prompt = prompt_template.replace("[user input]", user_theme)\
                                       .replace("[detail_json]", detail_content)
                                       
        print("\n==== 生成的提示 ====")
        print(final_prompt)
        print("===================\n")
        
        # API配置
        API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={google_api_key}"
        
        while True:
            try:
                print("正在请求 API...")
                headers = {
                    "Content-Type": "application/json"
                }
                payload = {
                    "contents": [{
                        "parts": [{"text": final_prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7
                    }
                }
                response = requests.post(API_URL, json=payload, headers=headers, timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # 清理 think 标签和markdown代码块
                    cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                    # 移除markdown代码块标记
                    cleaned_content = re.sub(r'```json\s*', '', cleaned_content)
                    cleaned_content = re.sub(r'```\s*$', '', cleaned_content)
                    cleaned_content = cleaned_content.strip()
                    
                    # 验证JSON格式
                    try:
                        script_data = json.loads(cleaned_content)
                        print("\n==== 有效脚本 ====")
                        print(json.dumps(script_data, indent=2, ensure_ascii=False))
                        print("==================")
                        return {
                            "script": script_data,
                            "title": user_theme
                        }
                    except json.JSONDecodeError as e:
                        print("\n生成的脚本格式无效：")
                        print(cleaned_content)
                        print(f"解析错误：{str(e)}")
                else:
                    print(f"请求失败，状态码：{response.status_code}")
                    print(f"错误响应：{response.text[:200]}...")
                    
            except requests.exceptions.RequestException as e:
                print(f"网络请求异常：{str(e)}")
            
            choice = input("\n是否重新生成？(y/n): ").lower()
            if choice != 'y':
                print("退出程序。")
                return None
                
    except FileNotFoundError:
        print("错误：找不到 prompt.txt 文件")
    except Exception as e:
        print(f"发生未知错误：{str(e)}")

if __name__ == "__main__":
    get_script()