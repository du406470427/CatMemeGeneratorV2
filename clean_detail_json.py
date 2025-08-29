import json
import os

def clean_detail_json():
    # 读取detail.json
    detail_path = './memes/detail.json'
    with open(detail_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'原始素材数量: {len(data)}')
    
    # 过滤出有效的素材（存在PNG目录的）
    valid_assets = []
    invalid_assets = []
    
    for item in data:
        asset_id = item['id']
        asset_dir = f'./memes/{asset_id}'
        
        # 检查素材目录是否存在且包含PNG文件
        if os.path.exists(asset_dir):
            png_files = [f for f in os.listdir(asset_dir) if f.endswith('.png')]
            if png_files:
                valid_assets.append(item)
            else:
                invalid_assets.append(asset_id)
        else:
            invalid_assets.append(asset_id)
    
    print(f'有效素材数量: {len(valid_assets)}')
    print(f'无效素材数量: {len(invalid_assets)}')
    
    # 备份原文件
    backup_path = './memes/detail.json.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'原文件已备份到: {backup_path}')
    
    # 保存清理后的文件
    with open(detail_path, 'w', encoding='utf-8') as f:
        json.dump(valid_assets, f, ensure_ascii=False, indent=2)
    
    print(f'已清理detail.json，保留 {len(valid_assets)} 个有效素材')
    
    # 显示前10个被移除的素材
    print('\n被移除的素材示例:')
    for i, asset_id in enumerate(invalid_assets[:10]):
        print(f'{i+1:2d}. {asset_id}')
    
    if len(invalid_assets) > 10:
        print(f'... 还有 {len(invalid_assets) - 10} 个被移除')

if __name__ == '__main__':
    clean_detail_json()