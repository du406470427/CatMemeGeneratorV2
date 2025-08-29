#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试视频转换问题
"""

import cv2
import numpy as np
import os
import tempfile
import shutil

def remove_green_background(frame, threshold=50):
    """
    移除绿幕背景，返回RGBA格式
    """
    # 转换为HSV色彩空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 定义绿色范围
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    
    # 创建绿色掩码
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # 形态学操作，去除噪点
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 创建RGBA图像
    rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    
    # 设置透明度：绿色区域为透明，其他区域为不透明
    rgba[:, :, 3] = 255 - mask
    
    return rgba

def find_content_bounds(frames):
    """
    找到所有帧中非透明内容的边界
    """
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = 0, 0
    
    for frame in frames:
        # 找到非透明像素
        alpha = frame[:, :, 3]
        coords = np.where(alpha > 0)
        
        if len(coords[0]) > 0:
            y_coords, x_coords = coords
            min_x = min(min_x, x_coords.min())
            min_y = min(min_y, y_coords.min())
            max_x = max(max_x, x_coords.max())
            max_y = max(max_y, y_coords.max())
    
    # 确保边界有效
    if min_x == float('inf'):
        return 0, 0, 100, 100
    
    return int(min_x), int(min_y), int(max_x), int(max_y)

def debug_single_video(video_path, output_dir):
    """
    调试单个视频的转换过程
    """
    print(f"调试视频: {video_path}")
    
    # 检查文件是否存在
    if not os.path.exists(video_path):
        print(f"错误: 文件不存在 {video_path}")
        return False
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理中文路径问题
    temp_video = None
    if os.name == 'nt':
        try:
            temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(temp_dir, "temp_debug.mp4")
            shutil.copy2(video_path, temp_video)
            cap = cv2.VideoCapture(temp_video)
            print(f"使用临时文件: {temp_video}")
        except Exception as e:
            print(f"创建临时文件失败: {e}")
            cap = cv2.VideoCapture(video_path)
    else:
        cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"错误: 无法打开视频文件")
        return False
    
    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"视频信息: {width}x{height}, {fps}fps, {frame_count}帧")
    
    frames = []
    frame_idx = 0
    
    # 提取前10帧进行测试
    while frame_idx < min(10, frame_count):
        ret, frame = cap.read()
        if not ret:
            print(f"读取帧 {frame_idx} 失败")
            break
        
        print(f"处理帧 {frame_idx}: {frame.shape}")
        
        # 移除绿幕背景
        rgba_frame = remove_green_background(frame)
        frames.append(rgba_frame)
        
        # 保存原始帧用于调试
        debug_path = os.path.join(output_dir, f"debug_original_{frame_idx:04d}.png")
        cv2.imwrite(debug_path, frame)
        
        # 保存处理后的帧
        debug_rgba_path = os.path.join(output_dir, f"debug_rgba_{frame_idx:04d}.png")
        cv2.imwrite(debug_rgba_path, rgba_frame)
        
        frame_idx += 1
    
    cap.release()
    
    if not frames:
        print("错误: 没有提取到任何帧")
        return False
    
    print(f"成功提取 {len(frames)} 帧")
    
    # 找到内容边界
    min_x, min_y, max_x, max_y = find_content_bounds(frames)
    print(f"内容边界: ({min_x}, {min_y}) 到 ({max_x}, {max_y})")
    
    # 处理帧
    target_size = 512
    png_dir = os.path.join(output_dir, "png")
    os.makedirs(png_dir, exist_ok=True)
    
    for i, frame in enumerate(frames):
        # 裁剪到内容区域
        cropped = frame[min_y:max_y+1, min_x:max_x+1]
        print(f"帧 {i} 裁剪后尺寸: {cropped.shape}")
        
        # 计算缩放比例
        h, w = cropped.shape[:2]
        scale = min(target_size / w, target_size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # 缩放
        resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
        print(f"帧 {i} 缩放后尺寸: {resized.shape}")
        
        # 创建目标画布
        canvas = np.zeros((target_size, target_size, 4), dtype=np.uint8)
        
        # 居中放置
        start_y = (target_size - new_h) // 2
        start_x = (target_size - new_w) // 2
        canvas[start_y:start_y+new_h, start_x:start_x+new_w] = resized
        
        # 保存最终帧
        output_path = os.path.join(png_dir, f"{i:04d}.png")
        success = cv2.imwrite(output_path, canvas)
        print(f"保存帧 {i}: {output_path}, 成功: {success}")
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"  文件大小: {file_size} bytes")
        else:
            print(f"  保存失败!")
    
    # 清理临时文件
    if temp_video and os.path.exists(temp_video):
        try:
            os.remove(temp_video)
            os.rmdir(os.path.dirname(temp_video))
        except:
            pass
    
    return True

def main():
    # 测试一个具体的视频文件
    video_path = "./memes/猫meme小剧场/B 对话&打架类/B1 紧张对视猫 .mp4"
    output_dir = "./debug_output"
    
    print("=== 调试视频转换 ===")
    debug_single_video(video_path, output_dir)

if __name__ == '__main__':
    main()