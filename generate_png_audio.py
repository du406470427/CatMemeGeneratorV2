import os
import cv2
import time
import numpy as np
import tempfile
import subprocess
import moviepy.editor as mpy
from skimage.measure import find_contours
from PIL import Image

def get_valid_directory():
    while True:
        path = input("请输入要处理的视频目录路径：").strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        path = os.path.normpath(path)
        if os.path.isdir(path):
            return os.path.abspath(path)
        print(f"路径无效或不存在：{path}")

def print_progress(current, total, start_time, prefix=""):
    elapsed = time.time() - start_time
    progress = current / total
    eta = elapsed / progress - elapsed if progress > 0 else 0
    print(f"\r{prefix} 进度：{current}/{total} [{progress:.1%}] 已用：{elapsed:.1f}s 剩余：{eta:.1f}s", end="")

def get_background_hsv(frame, sample_size=100):
    sample = frame[:sample_size, :sample_size]
    hsv = cv2.cvtColor(sample, cv2.COLOR_BGR2HSV)
    
    h = hsv[:,:,0].flatten()
    s = hsv[:,:,1].flatten()
    v = hsv[:,:,2].flatten()
    
    return (
        max(0, np.percentile(h, 5) - 5),
        max(0, np.percentile(s, 5) - 10),
        max(0, np.percentile(v, 5) - 10),
        min(180, np.percentile(h, 95) + 5),
        min(255, np.percentile(s, 95) + 10),
        min(255, np.percentile(v, 95) + 10)
    )

def create_alpha_channel(frame, bg_hsv_range):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower = np.array([bg_hsv_range[0], bg_hsv_range[1], bg_hsv_range[2]])
    upper = np.array([bg_hsv_range[3], bg_hsv_range[4], bg_hsv_range[5]])
    
    mask = cv2.inRange(hsv, lower, upper)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 消除绿边
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30,30))
    mask = cv2.dilate(mask, dilate_kernel, iterations=1)
    
    # 平滑边缘
    mask = cv2.GaussianBlur(mask, (7,7), 0)
    
    return cv2.bitwise_not(mask)

def find_content_boundary(alpha):
    contours = find_contours(alpha > 127)
    if not contours:
        return None
    all_points = np.vstack(contours)
    padding = 5
    x_min = max(0, np.min(all_points[:,1]) - padding)
    y_min = max(0, np.min(all_points[:,0]) - padding)
    x_max = min(alpha.shape[1], np.max(all_points[:,1]) + padding)
    y_max = min(alpha.shape[0], np.max(all_points[:,0]) + padding)
    return (x_min, y_min, x_max, y_max)

def safe_save_png(image_array, output_path):
    try:
        if image_array.shape[2] == 4:
            mode = 'RGBA'
        else:
            mode = 'RGB'
            
        pil_image = Image.fromarray(image_array, mode)
        pil_image.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"\n保存失败详细信息：")
        print(f"路径类型：{type(output_path)}")
        print(f"路径存在：{os.path.exists(os.path.dirname(output_path))}")
        print(f"路径可写：{os.access(os.path.dirname(output_path), os.W_OK)}")
        print(f"图像尺寸：{image_array.shape if image_array is not None else '空图像'}")
        print(f"错误类型：{type(e).__name__}")
        print(f"错误信息：{str(e)}")
        return False

def process_video(input_path, output_dir):
    try:
        start_time = time.time()
        print(f"\n{'='*40}")
        print(f"开始处理: {os.path.basename(input_path)}")
        
        clip = mpy.VideoFileClip(input_path)
        fps = clip.fps
        total_frames = int(clip.fps * clip.duration)
        
        original_base = os.path.splitext(os.path.basename(input_path))[0]
        safe_base = original_base
        fps_rounded = int(round(fps))
        base_name_with_fps = f"{safe_base}_{fps_rounded}fps"
        
        video_output_dir = os.path.join(output_dir, base_name_with_fps)
        png_dir = os.path.join(video_output_dir, "png")
        os.makedirs(png_dir, exist_ok=True)
        if not os.path.exists(png_dir):
            raise RuntimeError(f"无法创建目录：{png_dir}")
        
        audio_path = os.path.join(video_output_dir, "audio.wav")

        with tempfile.TemporaryDirectory() as temp_dir:
            # 分析绿幕颜色范围
            first_frame = clip.get_frame(0)
            bg_hsv_range = get_background_hsv(first_frame)
            print(f"背景HSV范围: H({bg_hsv_range[0]:.0f}-{bg_hsv_range[3]:.0f}) "
                  f"S({bg_hsv_range[1]:.0f}-{bg_hsv_range[4]:.0f}) "
                  f"V({bg_hsv_range[2]:.0f}-{bg_hsv_range[5]:.0f})")

            print("[1/3] 分析内容边界...")
            temp_frame_dir = os.path.join(temp_dir, "frames")
            os.makedirs(temp_frame_dir, exist_ok=True)
            boundaries = []
            
            for i, frame in enumerate(clip.iter_frames(dtype=np.uint8)):
                alpha = create_alpha_channel(frame, bg_hsv_range)
                rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                rgba[:, :, 3] = alpha
                
                temp_path = os.path.join(temp_frame_dir, f"frame_{i:05d}.png")
                if not cv2.imwrite(temp_path, rgba):
                    raise RuntimeError(f"无法写入临时帧: {temp_path}")
                
                bounds = find_content_boundary(alpha)
                if bounds:
                    boundaries.append(bounds)
                print_progress(i+1, total_frames, start_time, "边界分析")

            if not boundaries:
                raise ValueError("未检测到有效内容区域")

            # 计算全局裁切区域
            x_mins, y_mins, x_maxs, y_maxs = zip(*boundaries)
            crop_x = int(min(x_mins))
            crop_y = int(min(y_mins))
            crop_w = int(max(x_maxs) - crop_x)
            crop_h = int(max(y_maxs) - crop_y)
            print(f"\n裁切区域: X:{crop_x} Y:{crop_y} W:{crop_w} H:{crop_h}")

            print("[2/3] 生成最终PNG序列...")
            for i in range(total_frames):
                temp_path = os.path.join(temp_frame_dir, f"frame_{i:05d}.png")
                if not os.path.exists(temp_path):
                    print(f"\n警告：缺失帧 {temp_path}")
                    continue
                
                img = cv2.imread(temp_path, cv2.IMREAD_UNCHANGED)
                if img is None:
                    print(f"\n错误：无法读取帧 {temp_path}")
                    continue
                
                if img.size == 0:
                    print(f"\n错误：空图像数据在帧 {i}")
                    continue
                
                img_h, img_w = img.shape[:2]
                if (crop_y + crop_h > img_h) or (crop_x + crop_w > img_w):
                    print(f"\n警告：帧 {i} 裁切区域越界，使用安全裁切")
                    crop_y = max(0, min(crop_y, img_h - 1))
                    crop_x = max(0, min(crop_x, img_w - 1))
                    crop_h = max(1, min(crop_h, img_h - crop_y))
                    crop_w = max(1, min(crop_w, img_w - crop_x))
                
                cropped = img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
                
                max_size = 500
                height, width = cropped.shape[:2]
                if width == 0 or height == 0:
                    print(f"\n错误：无效图像尺寸 {width}x{height} 在帧 {i}")
                    continue
                
                scale = min(max_size/width, max_size/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                resized = cv2.resize(cropped, (new_width, new_height), interpolation=cv2.INTER_AREA)

                canvas = np.zeros((500, 500, 4), dtype=np.uint8)
                x_offset = (500 - new_width) // 2
                y_offset = (500 - new_height) // 2
                canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized

                output_path = os.path.join(png_dir, f"{i:05d}.png")
                if not safe_save_png(canvas, output_path):
                    print(f"\n错误：无法保存 {output_path}")
                print_progress(i+1, total_frames, start_time, "PNG生成")

            print("\n[3/3] 提取音频...")
            if clip.audio is not None:
                subprocess.run([
                    'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                    '-i', input_path,
                    '-vn', '-acodec', 'pcm_s16le',
                    '-ar', '44100', '-ac', '2',
                    audio_path
                ], check=True)
                print(f"音频已保存至 {audio_path}")
            else:
                print("未检测到音频轨道，跳过音频提取")

        print(f"\n处理完成！输出目录：{video_output_dir}")
        print(f"总耗时: {time.time()-start_time:.1f}秒")

    except subprocess.CalledProcessError as e:
        error_msg = f"""
        FFmpeg命令执行失败！
        命令: {' '.join(e.cmd)}
        错误代码: {e.returncode}
        错误输出: {e.stderr.decode() if e.stderr else '无'}
        """
        print(error_msg)
    except Exception as e:
        print(f"\n! 处理失败: {input_path}")
        print(f"错误信息: {str(e)}")
    finally:
        if 'clip' in locals():
            clip.close()

if __name__ == "__main__":
    print("=== 视频处理程序 ===")
    target_dir = get_valid_directory()
    output_dir = os.path.join(target_dir, "opt")
    
    video_files = []
    for root, _, files in os.walk(target_dir):
        if os.path.abspath(root) == os.path.abspath(output_dir):
            continue
        for f in files:
            if f.lower().endswith((".mp4", ".mov", ".avi")):
                video_files.append(os.path.join(root, f))
    
    if video_files:
        input("\n按 Enter 开始处理...")
        for video in video_files:
            process_video(video, output_dir)
        print("\n所有视频处理完成！输出目录：", output_dir)
    else:
        print("未找到支持的视频文件（支持格式：MP4/MOV/AVI）")