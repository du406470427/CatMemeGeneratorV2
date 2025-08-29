import os
import json
import textwrap
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import subprocess
from pydub import AudioSegment
import tempfile
import io
import re
from time import sleep
from get_script import get_script

class VideoGenerator:
    def __init__(self, script_json, title, output_dir="output", fps=24, resolution=(1080, 1440), pexels_api_key=None):
        self.script = json.loads(script_json) if isinstance(script_json, str) else script_json
        self.title = self._sanitize_filename(title)
        self.output_dir = os.path.join(output_dir, self.title)
        self.output_path = os.path.join(self.output_dir, "output.mp4")
        self.fps = fps
        self.width, self.height = resolution
        self.pexels_api_key = pexels_api_key
        self.temp_dir = tempfile.mkdtemp()
        self.video_clips = {}
        
        self.background_cache_pool = {}  # 图片缓存池
        self.cache_log_recorder = set()  # 缓存日志
        
        # 初始化字体
        try:
            self.subtitle_font = ImageFont.truetype("font.ttf", 60)
            self.title_font = ImageFont.truetype("font.ttf", 70)
        except IOError:
            self.subtitle_font = ImageFont.load_default(size=60)
            self.title_font = ImageFont.load_default(size=70)
            print("警告：未找到 font.ttf，使用默认字体替代")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def _sanitize_filename(self, filename):
        illegal_chars = r'[\\/*?:"<>|]'
        sanitized = re.sub(illegal_chars, "_", filename)
        # 限制最大长度
        return sanitized[:50].strip()

    def download_background(self, query):
        if not self.pexels_api_key:
            raise ValueError("需要Pexels API密钥")

        # 缓存命中判断
        if query in self.background_cache_pool:
            # 首次命中时打印日志
            if query not in self.cache_log_recorder:
                print(f"[缓存命中] 背景图片: {query}")
                self.cache_log_recorder.add(query)
            return self.background_cache_pool[query]
            
        print(f"[开始下载] 背景图片: {query}")
        headers = {"Authorization": self.pexels_api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=portrait"

        max_retries = 10
        for retry in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("photos"):
                    raise Exception(f"未找到相关图片: {query}")
                    
                # 获取质量最佳的图片
                photo_url = data["photos"][0]["src"]["original"]
                
                # 下载图片
                img_response = requests.get(photo_url, timeout=15)
                img_response.raise_for_status()
                
                # 处理图片
                img = Image.open(io.BytesIO(img_response.content)).convert("RGBA")
                img = self._process_image(img)
                
                # 更新缓存
                self.background_cache_pool[query] = img
                print(f"[下载成功] 背景图片: {query} (第{retry+1}次尝试)")
                
                sleep(1 if retry == 0 else 2**retry)
                return img
                
            except Exception as e:
                print(f"[下载失败] 第{retry+1}次尝试: {str(e)}")
                if retry == max_retries - 1:
                    print(f"[警告] 使用黑色背景替代: {query}")
                    return Image.new("RGBA", (self.width, self.height), (0,0,0,255))
                sleep(3)

    def _process_image(self, img):
        # 修改尺寸
        if img.size != (self.width, self.height):
            img = img.resize((self.width, self.height), Image.LANCZOS)

        img = img.convert("RGB")
        return img.convert("RGBA")

    def load_asset_frame(self, fg, frame_number):
        from moviepy.editor import VideoFileClip
        from moviepy.video.fx import all as vfx

        asset_id = fg['id']
        asset_path = os.path.join("./memes", asset_id)
        
        # 优先寻找视频文件
        video_file_path = None
        if os.path.isdir(asset_path):
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
            video_file_path_candidates = [os.path.join(asset_path, f) for f in os.listdir(asset_path) if any(f.lower().endswith(ext) for ext in video_extensions)]
            if video_file_path_candidates:
                video_file_path = video_file_path_candidates[0]

        if video_file_path:
            if asset_id not in self.video_clips:
                clip = VideoFileClip(video_file_path)
                # 处理绿幕
                if 'mask_color' in fg:
                    try:
                        mask_color = tuple(fg['mask_color'])
                        # 使用更安全的参数
                        clip = clip.fx(vfx.mask_color, color=mask_color, thr=fg.get('mask_thr', 20), s=fg.get('mask_s', 5))
                    except Exception as e:
                        print(f"绿幕处理失败 for {asset_id}: {e}")
                self.video_clips[asset_id] = clip

            clip = self.video_clips[asset_id]
            
            frame_time = frame_number / self.fps
            
            # 循环播放
            if clip.duration and frame_time >= clip.duration:
                frame_time = frame_time % clip.duration
            elif not clip.duration: # 处理单帧视频或图片
                frame_time = 0

            video_frame = clip.get_frame(frame_time)
            return Image.fromarray(video_frame).convert("RGBA")

        # 如果没有视频，则回退到PNG序列
        png_dir = os.path.join(asset_path, "png")
        if os.path.exists(png_dir):
            asset_frame = int(frame_number * (60 / self.fps))
            frame_file = f"{asset_frame:05d}.png"
            frame_path = os.path.join(png_dir, frame_file)

            if not os.path.exists(frame_path):
                png_files = sorted([f for f in os.listdir(png_dir) if f.endswith('.png')])
                if png_files:
                    frame_path = os.path.join(png_dir, png_files[-1])
                else:
                    raise FileNotFoundError(f"素材帧缺失: {asset_id}")
            
            return Image.open(frame_path).convert("RGBA")
            
        raise FileNotFoundError(f"找不到素材 '{asset_id}' 的视频文件或PNG序列")

    def generate_title_frame(self):
        title_frame = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(title_frame)
        
        # 颜色
        dark_yellow = (204, 153, 0, 255)
        text_color = (255, 255, 255, 255)
        
        # 间距
        top_margin = 30          
        horizontal_padding = 50  
        vertical_padding = 20    
        
        # 计算标题文字大小
        text_bbox = draw.textbbox((0, 0), self.title, font=self.title_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算标题背景尺寸
        bg_width = min(text_width + 2*horizontal_padding, self.width-40)
        bg_height = text_height + 2*vertical_padding
        bg_x = (self.width - bg_width) // 2
        bg_y = top_margin
        
        # 绘制标题背景
        draw.rounded_rectangle(
            [(bg_x, bg_y), (bg_x+bg_width, bg_y+bg_height)],
            radius=15,
            fill=dark_yellow
        )
        
        # 计算标题位置
        text_x = bg_x + (bg_width - text_width) // 2
        text_y = bg_y + vertical_padding - text_bbox[1]
        
        # 绘制标题文字
        draw.text((text_x, text_y), self.title, fill=text_color, font=self.title_font)
        
        return title_frame

    def generate_subtitle_frame(self, text, position, fg_size):
        subtitle_frame = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(subtitle_frame)
        
        # 每 7 个字换行
        max_chars_per_line = 7
        wrapped_text = textwrap.fill(text, width=max_chars_per_line)
        
        # 计算边界
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=self.subtitle_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 水平定位
        text_x = position['x'] - text_width // 2
        text_x = max(10, min(text_x, self.width - text_width - 10))
        
        # 垂直定位
        if position['y'] - text_height - 30 < 110:
            text_y = position['y'] + fg_size[1] // 2 + 30
        else:
            text_y = position['y'] - fg_size[1] // 2 - text_height - 30
            
        # 边界安全检测
        text_y = max(110, min(text_y, self.height - text_height - 10))
        
        # 设置文字描边
        offsets = [(dx, dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2) if dx or dy]
        for dx, dy in offsets:
            draw.text((text_x+dx, text_y+dy), wrapped_text, fill=(0,0,0,255), font=self.subtitle_font)
            
        # 绘制文字
        draw.text((text_x, text_y), wrapped_text, fill=(255,255,255,255), font=self.subtitle_font)
        
        return subtitle_frame

    def extract_audio(self, asset_id, duration):
        audio_path = os.path.join("./memes", asset_id, "audio.wav")
        if not os.path.exists(audio_path):
            return None
            
        audio = AudioSegment.from_wav(audio_path)
        return audio[:duration*1000]  # 精确到毫秒

    def generate_frame(self, scene, frame_time):
        try:
            bg_image = self.download_background(scene['background_image'])
        except Exception as e:
            print(f"背景加载失败: {str(e)}")
            bg_image = Image.new("RGBA", (self.width, self.height), (0,0,0,255))
            
        frame = bg_image.copy()
        scene_start = scene['start_time']
        frame_number = int((frame_time - scene_start) * self.fps)
        
        # 处理所有前景
        for fg in scene['foregrounds']:
            asset_id = fg['id']
            try:
                # 加载和缩放素材
                asset_img = self.load_asset_frame(fg, frame_number)
                scale_factor = fg['scale'] / 100.0
                new_size = (int(500*scale_factor), int(500*scale_factor))
                asset_img = asset_img.resize(new_size, Image.LANCZOS)
                
                # 定位中心点
                x = fg['position']['x'] - new_size[0]//2
                y = fg['position']['y'] - new_size[1]//2
                frame.paste(asset_img, (x, y), asset_img)
                
                # 处理字幕
                if 'subtitle' in fg and fg['subtitle']:
                    subtitle_layer = self.generate_subtitle_frame(
                        fg['subtitle'],
                        fg['position'],
                        new_size
                    )
                    frame = Image.alpha_composite(frame, subtitle_layer)
            except Exception as e:
                print(f"[素材异常] {asset_id}: {str(e)}")
                
        # 合成标题栏
        title_layer = self.generate_title_frame()
        frame = Image.alpha_composite(frame, title_layer)
        
        return np.array(frame.convert("RGB"))

    def merge_audio(self, video_path):
        total_duration = self.script[-1]['end_time']
        final_audio = AudioSegment.silent(duration=total_duration*1000)
        
        print("\n==== 开始音频混合 ====")
        audio_clip_count = 0
        for scene_idx, scene in enumerate(self.script):
            start = scene['start_time']
            scene_duration = scene['end_time'] - start
            print(f"处理场景 {scene_idx+1}/{len(self.script)} (时长: {scene_duration}s)")
            
            # 只处理第一个素材的音频
            for fg_idx, fg in enumerate(scene['foregrounds']):
                if fg_idx != 0:
                    print(f"跳过前景 {fg_idx+1} 的音频（非首个素材）")
                    continue
                    
                print(f"处理前景 {fg_idx+1} ({fg['id']})...", end='', flush=True)
                audio_clip = self.extract_audio(fg['id'], scene_duration)
                if audio_clip:
                    try:
                        final_audio = final_audio.overlay(audio_clip, position=int(start*1000))
                        audio_clip_count += 1
                        print(f"已添加 {len(audio_clip)}ms 音频")
                    except Exception as e:
                        print(f"音频混合失败: {str(e)}")
                else:
                    print("无可用音频")
        
        # 生成临时音频
        audio_path = os.path.abspath(os.path.join(self.temp_dir, "final_audio.wav"))
        print(f"\n导出音频到: {audio_path}")
        
        try:
            # 测试目录存在
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            # 导出失败时最多重试 3 次
            max_export_retries = 3
            for retry in range(max_export_retries):
                try:
                    final_audio.export(audio_path, format="wav")
                    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1024:
                        print(f"音频导出成功 ({os.path.getsize(audio_path)//1024}KB)")
                        break
                    else:
                        raise ValueError("音频文件生成异常")
                except Exception as e:
                    if retry == max_export_retries -1:
                        raise RuntimeError(f"音频导出失败: {str(e)}")
                    print(f"音频导出重试 {retry+1}/{max_export_retries}")
                    sleep(1)
                    
        except Exception as e:
            print(f"错误: {str(e)}")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            raise
        
        # 测试视频存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件丢失: {video_path}")
        
        # 尝试使用moviepy进行音视频合成（避免ffmpeg依赖问题）
        print("\n==== 使用MoviePy合成音视频 ====")
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            
            # 加载视频和音频
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            # 合成音视频
            final_clip = video_clip.set_audio(audio_clip)
            
            # 导出最终视频
            final_clip.write_videofile(
                self.output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # 清理资源
            final_clip.close()
            video_clip.close()
            audio_clip.close()
            
            print("MoviePy合成成功！")
            
        except Exception as e:
            print(f"MoviePy合成失败: {str(e)}")
            print("尝试使用FFmpeg...")
            
            # 回退到ffmpeg
            def win_long_path(path):
                return "\\\\?\\" + os.path.abspath(path) if os.name == 'nt' else path
            
            cmd = [
                'ffmpeg', '-y',
                '-i', win_long_path(video_path),
                '-i', win_long_path(audio_path),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                win_long_path(self.output_path)
            ]
            
            print("\n==== 执行FFmpeg命令 ====")
            print(" ".join(cmd))
            
            try:
                result = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                print("FFmpeg合成成功！")
            except subprocess.CalledProcessError as e:
                error_msg = f"""
                FFmpeg合成失败！
                命令：{' '.join(cmd)}
                退出代码：{e.returncode}
                错误输出：
                {e.stderr}
                """
                print(error_msg)
                
                debug_dir = os.path.join(self.output_dir, "debug_files")
                os.makedirs(debug_dir, exist_ok=True)
                os.replace(video_path, os.path.join(debug_dir, "temp_video.mp4"))
                os.replace(audio_path, os.path.join(debug_dir, "final_audio.wav"))
                print(f"调试文件已保存到: {debug_dir}")
                
                raise RuntimeError("视频合成失败，请检查调试文件") from e
        finally:
            # 清理临时文件
            def safe_remove(path):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        print(f"清理临时文件: {path}")
                except Exception as e:
                    print(f"清理文件失败 {path}: {str(e)}")
                    
            safe_remove(video_path)
            safe_remove(audio_path)

    def generate_video(self):
        try:
            total_duration = self.script[-1]['end_time']
            total_frames = int(total_duration * self.fps)
            temp_video = os.path.abspath(os.path.join(self.temp_dir, "temp_video.mp4"))
            
            os.makedirs(self.temp_dir, exist_ok=True)
            if os.name == 'nt':
                os.chmod(self.temp_dir, 0o777)
                            
        except Exception as e:
            print(f"\n生成过程中断: {str(e)}")
            print("尝试保留临时文件...")
            debug_dir = os.path.join(self.output_dir, "partial_output")
            os.makedirs(debug_dir, exist_ok=True)
            
            if os.path.exists(temp_video):
                os.replace(temp_video, os.path.join(debug_dir, "partial_video.mp4"))
            if hasattr(self, 'temp_dir'):
                print(f"临时文件目录: {self.temp_dir}")
            
            raise

    def generate_video(self):
        total_duration = self.script[-1]['end_time']
        total_frames = int(total_duration * self.fps)
        temp_video = os.path.join(self.temp_dir, "temp_video.mp4")
        
        # 初始化 writer
        writer = cv2.VideoWriter(
            temp_video,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            (self.width, self.height)
        )
        
        # 逐帧生成
        for frame_idx in range(total_frames):
            current_time = frame_idx / self.fps
            current_scene = next(
                (s for s in self.script if s['start_time'] <= current_time < s['end_time']),
                None
            )
            
            if current_scene:
                frame = self.generate_frame(current_scene, current_time)
            else:
                # 处理空白帧
                frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                title_layer = self.generate_title_frame()
                frame_pil = Image.fromarray(frame).convert("RGBA")
                frame = np.array(Image.alpha_composite(frame_pil, title_layer).convert("RGB"))
                
            writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
        writer.release()
        self.merge_audio(temp_video)
        
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir)
        print(f"[生成完成] 输出文件: {self.output_path}")

if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成视频')
    parser.add_argument('--script', help='指定剧本JSON文件路径')
    args = parser.parse_args()
    
    # 从配置文件读取 API 密钥
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        pexels_api_key = config["pexels_api_key"]
    except FileNotFoundError:
        print("错误：未找到 config.json 配置文件")
        exit()
    except json.JSONDecodeError:
        print("错误：config.json 格式不正确")
        exit()
    except KeyError:
        print("错误：config.json 中缺少 pexels_api_key 字段")
        exit()

    # 获取剧本和标题
    if args.script:
        # 使用指定的剧本文件
        try:
            with open(args.script, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            video_title = "测试视频"
            print(f"使用剧本文件: {args.script}")
        except FileNotFoundError:
            print(f"错误：找不到剧本文件 {args.script}")
            exit()
        except json.JSONDecodeError:
            print(f"错误：剧本文件 {args.script} 格式不正确")
            exit()
    else:
        # 使用API生成剧本
        result = get_script()
        if not result:
            print("无法获取有效剧本，程序退出")
            exit()
        script_data = result["script"]
        video_title = result["title"]
    
    generator = VideoGenerator(
        script_data,
        title=video_title,
        output_dir="output",
        pexels_api_key=pexels_api_key
    )
    generator.generate_video()