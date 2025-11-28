import sys
import os
import json
import importlib.util
from flask import Flask, Response

# 确保能找到 base 包
sys.path.append(os.getcwd())

app = Flask(__name__)

def load_spider_class(filepath):
    """动态加载 Python 脚本中的 Spider 类"""
    try:
        # 获取模块名
        module_name = os.path.basename(filepath).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module.Spider
    except Exception as e:
        print(f"Error loading module {filepath}: {e}")
        return None

@app.route('/')
def index():
    return "<h1>IPTV Aggregator is Running on Zeabur</h1><p>M3U Link: <a href='/iptv.m3u'>/iptv.m3u</a></p>"

@app.route('/iptv.m3u')
def get_m3u():
    m3u_content = ["#EXTM3U"]
    
    # 读取配置文件
    try:
        with open('iptv.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        return f"Error reading iptv.json: {e}", 500

    for item in config.get('lives', []):
        name = item.get('name')
        # 处理路径：将 file://Download/xxx 转换为本地路径 Download/xxx
        api_path = item.get('api')
        if api_path.startswith('file://'):
            real_path = api_path.replace('file://', '')
        else:
            real_path = api_path

        # 确保路径存在
        if not os.path.exists(real_path):
            print(f"File not found: {real_path}")
            continue

        print(f"Running spider: {name} ({real_path})...")
        
        SpiderClass = load_spider_class(real_path)
        if SpiderClass:
            try:
                spider = SpiderClass()
                # 传入扩展参数
                ext_str = json.dumps(item.get('ext', {}))
                spider.init(ext_str)
                
                # 获取直播内容
                content = spider.liveContent(None)
                
                # 清理数据：移除重复的 #EXTM3U 头
                lines = content.split('\n')
                for line in lines:
                    if '#EXTM3U' in line:
                        continue
                    if line.strip():
                        m3u_content.append(line)
            except Exception as e:
                print(f"Error executing spider {name}: {e}")
                
    return Response('\n'.join(m3u_content), mimetype='text/plain; charset=utf-8')

if __name__ == '__main__':
    # Zeabur 可能会提供 PORT 环境变量
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
