#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量转换MP4绿幕素材为PNG帧序列
基于现有的generate_png_audio.py逻辑，专门处理猫meme小剧场素材
"""

import cv2
import numpy as np
import os
import json
import argparse
from pathlib import Path
import subprocess
import re

def remove_green_background(frame, threshold=50):
    """
    移除绿幕背景
    """
    # 转换为HSV色彩空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 定义绿色范围
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # 创建绿色掩码
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # 形态学操作，去除噪声
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 创建RGBA图像
    rgba_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    
    # 将绿色区域设为透明
    rgba_frame[:, :, 3] = 255 - mask
    
    return rgba_frame

def find_content_bounds(frames):
    """
    找到所有帧中内容的边界
    """
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = 0, 0
    
    for frame in frames:
        # 找到非透明像素
        alpha = frame[:, :, 3]
        coords = np.where(alpha > 0)
        
        if len(coords[0]) > 0:
            y_min, y_max = coords[0].min(), coords[0].max()
            x_min, x_max = coords[1].min(), coords[1].max()
            
            min_x = min(min_x, x_min)
            min_y = min(min_y, y_min)
            max_x = max(max_x, x_max)
            max_y = max(max_y, y_max)
    
    return int(min_x), int(min_y), int(max_x), int(max_y)

def extract_audio(video_path, output_path):
    """
    使用moviepy提取音频
    """
    try:
        # 首先尝试使用moviepy
        try:
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(video_path)
            if video.audio is not None:
                video.audio.write_audiofile(output_path, verbose=False, logger=None)
                video.close()
                return True
            else:
                print(f"视频文件没有音频轨道: {video_path}")
                video.close()
                return False
        except ImportError:
            print("moviepy未安装，尝试使用ffmpeg")
            # 回退到ffmpeg
            cmd = [
                'ffmpeg', '-i', video_path, 
                '-vn', '-acodec', 'pcm_s16le', 
                '-ar', '44100', '-ac', '2',
                '-y', output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=False)
            if result.returncode == 0:
                return True
            else:
                try:
                    stderr_msg = result.stderr.decode('utf-8', errors='replace')
                except:
                    stderr_msg = str(result.stderr)
                print(f"ffmpeg音频提取失败: {stderr_msg}")
                return False
    except Exception as e:
        print(f"音频提取异常: {e}")
        return False

def process_video(video_path, output_dir, asset_id):
    """
    处理单个视频文件
    """
    # 确保路径编码正确
    try:
        video_path_safe = os.path.normpath(video_path)
        print(f"处理视频: {video_path_safe}")
    except Exception as e:
        print(f"路径编码错误: {e}")
        return False
    
    # 创建输出目录
    asset_output_dir = output_dir
    os.makedirs(asset_output_dir, exist_ok=True)
    
    # 读取视频 - 修复中文路径问题
    try:
        # 在Windows上，使用原始字符串路径
        if os.name == 'nt':
            # 尝试使用短路径名避免中文编码问题
            import tempfile
            import shutil
            # 创建临时文件副本
            temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(temp_dir, f"temp_{asset_id}.mp4")
            shutil.copy2(video_path_safe, temp_video)
            cap = cv2.VideoCapture(temp_video)
        else:
            cap = cv2.VideoCapture(video_path_safe)
    except Exception as e:
        print(f"无法打开视频文件: {e}")
        return False
    
    frames = []
    
    # 提取所有帧
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 移除绿幕背景
        rgba_frame = remove_green_background(frame)
        frames.append(rgba_frame)
    
    cap.release()
    
    if not frames:
        print(f"警告: 无法从 {video_path_safe} 提取帧")
        return False
    
    # 找到内容边界
    min_x, min_y, max_x, max_y = find_content_bounds(frames)
    
    # 裁剪并缩放帧
    target_size = 512  # 目标尺寸
    processed_frames = []
    
    for frame in frames:
        # 裁剪到内容区域
        cropped = frame[min_y:max_y+1, min_x:max_x+1]
        
        # 计算缩放比例，保持宽高比
        h, w = cropped.shape[:2]
        scale = min(target_size / w, target_size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # 缩放
        resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 创建目标尺寸的透明画布
        canvas = np.zeros((target_size, target_size, 4), dtype=np.uint8)
        
        # 居中放置
        start_y = (target_size - new_h) // 2
        start_x = (target_size - new_w) // 2
        canvas[start_y:start_y+new_h, start_x:start_x+new_w] = resized
        
        processed_frames.append(canvas)
    
    # 保存PNG帧序列到png子目录
    png_dir = os.path.join(asset_output_dir, "png")
    os.makedirs(png_dir, exist_ok=True)
    
    for i, frame in enumerate(processed_frames):
        output_path = os.path.join(png_dir, f"{i:04d}.png")
        # 使用PIL保存RGBA格式的PNG
        try:
            from PIL import Image
            # 转换BGR+Alpha到RGBA
            rgba_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA)
            img = Image.fromarray(rgba_frame, 'RGBA')
            img.save(output_path, 'PNG')
            if i == 0:  # 只打印第一帧的成功信息
                print(f"PNG帧保存成功，示例: {output_path}")
        except Exception as e:
            print(f"警告: 保存帧 {i} 失败: {output_path}, 错误: {e}")
    
    # 验证PNG文件是否真的被创建
    png_files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
    print(f"PNG目录中实际文件数: {len(png_files)}")
    if len(png_files) == 0:
        print(f"错误: PNG目录为空! 目录路径: {png_dir}")
        print(f"目录是否存在: {os.path.exists(png_dir)}")
        print(f"目录权限: {os.access(png_dir, os.W_OK)}")
    
    # 提取音频
    audio_path = os.path.join(asset_output_dir, "audio.wav")
    # 使用安全的路径进行音频提取
    audio_source = temp_video if (os.name == 'nt' and 'temp_video' in locals()) else video_path_safe
    if extract_audio(audio_source, audio_path):
        print(f"音频提取成功: {asset_id}")
    else:
        print(f"音频提取失败: {asset_id}")
    
    # 最终清理临时文件
    if os.name == 'nt' and 'temp_video' in locals():
        try:
            if os.path.exists(temp_video):
                os.remove(temp_video)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except:
            pass
    
    print(f"完成处理: {asset_id}, 生成 {len(processed_frames)} 帧")
    return True

def main():
    parser = argparse.ArgumentParser(description='批量转换MP4绿幕素材为PNG帧序列')
    parser.add_argument('--input-dir', default='./memes/猫meme小剧场', help='输入目录路径')
    parser.add_argument('--output-dir', default='./memes', help='输出目录路径')
    parser.add_argument('--force', action='store_true', help='强制重新处理已存在的素材')
    parser.add_argument('--use-mapping', action='store_true', help='使用素材名称映射')
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    if not os.path.exists(input_dir):
        print(f"输入目录不存在: {input_dir}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 导入映射功能
    if args.use_mapping:
        try:
            from asset_mapping import create_name_mapping, get_asset_id_from_filename
            mapping = create_name_mapping()
            print("已加载素材名称映射")
        except ImportError:
            print("无法导入asset_mapping模块，使用默认命名")
            mapping = {}
    else:
        mapping = {}
    
    processed_count = 0
    
    # 遍历所有分类目录
    for category_dir in os.listdir(input_dir):
        category_path = os.path.join(input_dir, category_dir)
        if not os.path.isdir(category_path):
            continue
        
        print(f"处理分类: {category_dir}")
        
        # 遍历分类目录中的所有视频文件
        for filename in os.listdir(category_path):
            if not filename.lower().endswith(('.mp4', '.mov', '.avi')):
                continue
            
            video_path = os.path.join(category_path, filename)
            
            # 获取asset_id
            if mapping:
                asset_id = get_asset_id_from_filename(filename, mapping)
            else:
                # 使用文件名生成asset_id，确保正确处理中文字符
                base_name = os.path.splitext(filename)[0]
                # 先确保字符串是正确的UTF-8编码
                try:
                    # 如果文件名已经是正确的UTF-8，直接使用
                    base_name_utf8 = base_name
                    # 测试是否包含有效的中文字符
                    base_name_utf8.encode('utf-8')
                except UnicodeEncodeError:
                    # 如果编码有问题，尝试修复
                    try:
                        base_name_utf8 = base_name.encode('latin-1').decode('utf-8')
                    except:
                        base_name_utf8 = base_name
                
                # 使用更安全的字符替换方式
                import unicodedata
                # 保留中文字符、英文字母、数字
                clean_chars = []
                for char in base_name_utf8:
                    if char.isalnum() or '\u4e00' <= char <= '\u9fff':
                        clean_chars.append(char)
                    else:
                        clean_chars.append('_')
                asset_id = ''.join(clean_chars).lower()
                # 清理连续的下划线
                asset_id = re.sub(r'_+', '_', asset_id).strip('_')
            
            # 检查输出目录是否已存在
            asset_output_dir = os.path.join(output_dir, asset_id)
            if os.path.exists(asset_output_dir) and not args.force:
                print(f"跳过已存在的素材: {asset_id}")
                continue
            
            print(f"处理素材: {asset_id} ({filename})")
            
            if process_video(video_path, asset_output_dir, asset_id):
                processed_count += 1
            else:
                print(f"处理失败: {asset_id}")
    
    print(f"\n批量转换完成，共处理 {processed_count} 个素材")
    
    # 如果使用映射，更新detail.json
    if args.use_mapping:
        try:
            from asset_mapping import update_detail_json_with_mapping
            detail_path = os.path.join(output_dir, 'detail.json')
            update_detail_json_with_mapping(detail_path, mapping, input_dir)
        except ImportError:
            print("无法更新detail.json")

if __name__ == '__main__':
    main()