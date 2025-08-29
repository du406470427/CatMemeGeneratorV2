#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试视频生成功能
使用新添加的素材测试音频和视频是否能正确匹配
"""

import json
import os
from main import VideoGenerator

def create_test_script():
    """创建一个简单的测试剧本"""
    test_script = [
        {
            "start_time": 0,
            "end_time": 3,
            "foregrounds": [
                {
                    "id": "g1_对话猫",
                    "position": {"x": 540, "y": 720},
                    "scale": 100,
                    "subtitle": "你好！"
                }
            ],
            "background_image": "office"
        },
        {
            "start_time": 3,
            "end_time": 6,
            "foregrounds": [
                {
                    "id": "g3_爆笑猫",
                    "position": {"x": 540, "y": 720},
                    "scale": 100,
                    "subtitle": "哈哈哈！"
                }
            ],
            "background_image": "office"
        }
    ]
    return test_script

def test_asset_exists(asset_id):
    """测试素材是否存在"""
    asset_dir = os.path.join("./memes", asset_id)
    png_dir = os.path.join(asset_dir, "png")
    audio_file = os.path.join(asset_dir, "audio.wav")
    
    print(f"检查素材: {asset_id}")
    print(f"  目录存在: {os.path.exists(asset_dir)}")
    print(f"  PNG目录存在: {os.path.exists(png_dir)}")
    if os.path.exists(png_dir):
        png_files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
        print(f"  PNG帧数: {len(png_files)}")
    print(f"  音频文件存在: {os.path.exists(audio_file)}")
    if os.path.exists(audio_file):
        print(f"  音频文件大小: {os.path.getsize(audio_file)} bytes")
    print()

def main():
    print("=== 测试视频生成功能 ===")
    
    # 检查配置文件
    if not os.path.exists('config.json'):
        print("错误：未找到 config.json 配置文件")
        return
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    if 'pexels_api_key' not in config:
        print("错误：config.json 中缺少 pexels_api_key 字段")
        return
    
    # 测试素材是否存在
    test_assets = ["g1_对话猫", "g3_爆笑猫"]
    for asset_id in test_assets:
        test_asset_exists(asset_id)
    
    # 创建测试剧本
    test_script = create_test_script()
    
    print("创建视频生成器...")
    generator = VideoGenerator(
        test_script,
        title="测试视频",
        output_dir="output",
        pexels_api_key=config["pexels_api_key"]
    )
    
    print("开始生成视频...")
    try:
        generator.generate_video()
        print("\n=== 视频生成成功！ ===")
        print(f"输出文件: {generator.output_path}")
    except Exception as e:
        print(f"\n=== 视频生成失败 ===")
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()