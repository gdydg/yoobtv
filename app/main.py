import sys
import os
import json
import importlib.util
import logging
from flask import Flask, Response

# 配置日志，确保 Zeabur 控制台能看到
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_spider_class(filepath):
    """动态加载 Python 脚本中的 Spider 类"""
    try:
        if not os.path.exists(filepath):
            logger.error(f"文件不存在: {filepath}")
            return None

        # 获取模块名
        module_name = os.path.basename(filepath).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None or spec.loader is None:
            logger.error(f"无法加载模块规范: {filepath}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if hasattr(module, 'Spider'):
            return module.Spider
        else:
            logger.error(f"模块 {module_name} 中未找到 Spider 类")
            return None
    except Exception as e:
        logger.error(f"加载模块 {filepath} 出错: {e}")
        return None

@app.route('/')
def index():
    return "<h1>IPTV Service is Running</h1><p>Status: OK</p><p>Link: <a href='/iptv.m3u'>/iptv.m3u</a></p>"

@app.route('/iptv.m3u')
def get_m3u():
    m3u_content = ["#EXTM3U"]
    
    config_path = 'iptv.json'
    if not os.path.exists(config_path):
        return f"配置丢失: 找不到 {config_path}", 500

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        return f"配置错误: {e}", 500

    for item in config.get('lives', []):
        name = item.get('name')
        api_path = item.get('api')
        
        # 路径清理
        if api_path.startswith('file://'):
            real_path = api_path.replace('file://', '')
        else:
            real_path = api_path

        # 路径修正：如果是相对路径，确保基于当前工作目录
        if not os.path.isabs(real_path):
            real_path = os.path.join(os.getcwd(), real_path)

        logger.info(f"正在抓取: {name} (路径: {real_path})")
        
        SpiderClass = load_spider_class(real_path)
        if SpiderClass:
            try:
                spider = SpiderClass()
                ext_str = json.dumps(item.get('ext', {}))
                spider.init(ext_str)
                
                # 抓取内容
                content = spider.liveContent(None)
                
                # 清理重复的头
                if content:
                    lines = content.split('\n')
                    valid_lines = [line for line in lines if line.strip() and '#EXTM3U' not in line]
                    m3u_content.extend(valid_lines)
                else:
                    logger.warning(f"{name} 返回内容为空")

            except Exception as e:
                logger.error(f"执行爬虫 {name} 失败: {e}")
                # 可选：将错误显示在 m3u 中方便调试
                # m3u_content.append(f"#EXTINF:-1 group-title=\"错误\", {name} 抓取失败")
                # m3u_content.append("http://127.0.0.1/error")

    return Response('\n'.join(m3u_content), mimetype='text/plain; charset=utf-8')

# 移除 app.run，由 Gunicorn 启动
