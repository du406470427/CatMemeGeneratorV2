import json
import os

# 读取detail.json
with open('./memes/detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查缺失PNG目录的素材
missing = []
for item in data:
    asset_id = item['id']
    png_path = f'./memes/{asset_id}/png'
    if not os.path.exists(png_path):
        missing.append(asset_id)

print(f'缺失PNG目录的素材数量: {len(missing)}')
print('前20个缺失的素材:')
for i, asset_id in enumerate(missing[:20]):
    print(f'{i+1:2d}. {asset_id}')

if len(missing) > 20:
    print(f'... 还有 {len(missing) - 20} 个缺失素材')

# 检查只有音频没有PNG的素材
audio_only = []
for item in data:
    asset_id = item['id']
    asset_dir = f'./memes/{asset_id}'
    audio_path = f'{asset_dir}/audio.mp3'
    png_path = f'{asset_dir}/png'
    
    if os.path.exists(audio_path) and not os.path.exists(png_path):
        audio_only.append(asset_id)

print(f'\n只有音频没有PNG的素材数量: {len(audio_only)}')
for asset_id in audio_only[:10]:
    print(f'- {asset_id}')