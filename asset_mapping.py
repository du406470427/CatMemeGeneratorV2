#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材名称映射工具
根据素材文件名和语义，映射到detail.json中的对应ID
"""

import os
import json
import re
from pathlib import Path

def create_name_mapping():
    """创建素材名称到ID的映射关系"""
    mapping = {
        # A类 - 吃东西类
        "A1 喝AD钙猫.mov": "A1_drink_ad_calcium_cat",
        "A10 吃鱼干猫.mp4": "A10_eat_fish_snack_cat", 
        "A2 吃薯片猫.mp4": "A2_eat_chips_cat",
        "A3 咬东西猫 .mp4": "A3_bite_things_cat",
        "A5 咀嚼猫.mp4": "A5_chewing_cat",
        
        # B类 - 对话&打架类
        "B1 紧张对视猫 .mp4": "B1_nervous_stare_cat",
        "B11 试探猫猫.mp4": "B11_probe_cat",
        "B12 爆踹猫.mp4": "B12_kick_cat",
        "B13 拳击猫猫.mp4": "B13_boxing_cat",
        "B14 打枪猫.mp4": "B14_gun_cat",
        "B15 大舌头驴 .mp4": "B15_big_tongue_donkey",
        "B16 pop猫.mp4": "B16_pop_cat",
        "B17 疑惑对话.mp4": "B17_confused_dialogue",
        "B18 打拳猫.mp4": "B18_punch_cat",
        "B19 吵架猫.mp4": "B19_quarrel_cat",
        "B2 打头猫.mp4": "B2_hit_head_cat",
        "B20 帅气兄弟猫.mp4": "B20_handsome_brother_cat",
        
        # C类 - 工作&学习类
        "C1 打电脑猫.mp4": "C1_computer_cat",
        "C2 蓝衣服打电脑猫.mov": "C2_blue_shirt_computer_cat",
        "C3 打电脑狗.mp4": "C3_computer_dog",
        "C4 写字猫.mp4": "C4_writing_cat",
        "C5 客服猫 .mp4": "C5_customer_service_cat",
        "C6 学习猫.mp4": "C6_studying_cat",
        "C7 看报猫.mp4": "C7_reading_newspaper_cat",
        "C8 看书猫.mp4": "C8_reading_book_cat",
        
        # D类 - 骑车&驾驶类
        "D1 开车猫.mp4": "D1_driving_cat",
        "D2 骑摩托猫 .mp4": "D2_motorcycle_cat",
        "D3 骑小摩托猫 .mp4": "D3_small_motorcycle_cat",
        "D4 戴墨镜开车.mp4": "D4_sunglasses_driving",
        "D5 美猫骑毛驴.mp4": "D5_beauty_cat_riding_donkey",
        "D6 鼠鼠骑车.mp4": "D6_mouse_cycling",
        "D7 开车猫.mp4": "D7_driving_cat_2",
        
        # E类 - 生活行为类
        "E1 洗衣服猫.mp4": "E1_washing_clothes_cat",
        "E10 披风猫.mp4": "E10_cape_cat",
        "E100 闻味道猫.mp4": "E100_smell_cat",
        "E101 按摩猫.mp4": "E101_massage_cat",
        "E102 低头猫.mp4": "E102_bow_head_cat",
        "E103 弹跳猫.mp4": "E103_jumping_cat",
        "E104 走路猫.mp4": "E104_walking_cat",
        "E105 左右看猫.mp4": "E105_look_around_cat",
        
        # F类 - 情侣猫
        "F1 安慰猫.mp4": "F1_comfort_cat",
        "F10 同步摆头猫猫.mp4": "F10_sync_head_shake_cats",
        "F11 蹭蹭猫.mp4": "F11_nuzzle_cat",
        "F12 抱脖子猫.mp4": "F12_hug_neck_cat",
        "F13 亲亲头猫.mp4": "F13_kiss_head_cat",
        
        # 语义映射 - 根据素材名称含义映射到原有ID
        "E14 昏睡香蕉猫.mp4": "banana-like-cat-fainting",
        "E96 睡觉香蕉猫.mp4": "sleepy_cat",
        "E126 旋转香蕉猫.mp4": "cat_rotating",
        "E31 离家出走猫.mp4": "cat_carrying_a_bag",
        "E32 走路香蕉猫.mp4": "crying_banana-like-cat",
        "E6 生日快乐猫猫.mp4": "cat_dressing_in_chinese_new_year_style_dancing",
        "E122 旋转猫.mp4": "cat_rotating",
        "E124 自转猫.mp4": "cat_on_a_motor_rotating",
        "E82 打哈欠猫.mp4": "cat_yawning",
        "E106 胖胖哈欠猫.mp4": "cat_yawning",
        "E116 轮流打哈欠猫.mp4": "cat_yawning",
        "E30 哈欠丑猫.mp4": "cat_yawning",
        "E107 坐着猫.mp4": "cat_sitting",
        "E117 坐着猫.mp4": "cat_sitting",
        "E137 坐着猫.mov": "cat_sitting",
        "E97 盘腿猫.mp4": "cat_sitting",
        "E87 黑猫崩溃.mp4": "cat_holding_head_and_screaming",
        "E111 难受猫.mp4": "cat_feeling_wronged",
        "E66 求求猫.mp4": "cat_making_a_bow",
        "E93 求求猫.mp4": "cat_making_a_bow",
        "E95 求求猫2.mp4": "cat_making_a_bow",
        "E90 尖叫狗.mp4": "shouting_cat",
        "E26 话痨猫.mp4": "cat_rapidly_opening_and_closing_mouth",
        "E121 霸总猫.mp4": "serious_cat_questioning",
        "E8 走路.mp4": "cat_sitting",
        "E9 自信走路猫.mp4": "cat_sitting",
        "E7 嚣张猫走路.mp4": "cat_sitting",
        "E20 走路猫.mp4": "cat_sitting",
        "E67 走路猫.mp4": "cat_sitting",
        "E188 吓一跳猫.mp4": "shocked_cat",
        "E48 吓一跳猫.mp4": "shocked_cat",
        "E42 惆怅猫.mp4": "hopeless_cat",
        "E85 犯困猫.mp4": "sleepy_cat",
        "E94 犯困猫.mp4": "sleepy_cat",
        "E139 犯困猫.mov": "sleepy_cat",
        "E25 困困猫.mp4": "sleepy_cat",
        "E44 逐渐困猫.mp4": "sleepy_cat",
        "E71 逐渐昏睡猫.mp4": "sleepy_cat",
        "E15 没睡醒猫.mp4": "sleepy_cat",
        "E57 睡觉猫.mp4": "sleepy_cat",
        "E29 仰头睡觉猫.mp4": "sleepy_cat",
        "E47 玩手机睡觉猫.mp4": "sleepy_cat",
        "E43 被吵醒猫.mp4": "sleepy_cat",
        "B3 点头猫奶牛猫对话.mp4": "cat_gazing_at_another_cat",
        "B4 经典对话猫.mp4": "cat_gazing_at_another_cat",
        "B5 两只对视猫 .mp4": "cat_gazing_at_another_cat",
        "B7 紧张对视猫狗 .mp4": "cat_gazing_at_another_cat",
        "B8 霸总猫和愤怒猫.mp4": "angry_cat",
        "B9 听八卦的你.mp4": "cat_being_interviewed",
        "B6 打架猫.mp4": "a_cat_hitting_another_cat",
        "E49 武打猫.mp4": "a_cat_hitting_another_cat",
        "E146 功夫猫.mov": "a_cat_hitting_another_cat",
        "E50 暗中观察猫.mp4": "confused_cat",
        "E23 偷看小猫.mp4": "confused_cat",
        "E76 门后猫.mp4": "confused_cat",
        "E84 门后猫2.mp4": "confused_cat",
        "E60 左顾右盼猫.mp4": "confused_cat",
        "E33 捂眼睛猫.mp4": "curl_up_cat_shaking",
        "E46 做错事猫.mp4": "wet_upset_cat",
        "E40 脏脏猫.mp4": "wet_upset_cat",
        "E83 受伤猫.mp4": "wet_upset_cat",
        "E98 崴腿猫.mp4": "wet_upset_cat",
        "E69 摔倒猫.mp4": "wet_upset_cat",
        "E144 烧焦猫.mov": "wet_upset_cat",
        "E114 抽搐猫.mp4": "muddled_cat",
        "E86 龅牙猫.mp4": "muddled_cat",
        "E125 小獭闻猫.mp4": "sheep_sticking_out_tongue",
        "E99 妈妈鼠.mp4": "sheep_sticking_out_tongue",
        "E123 歪头狗.mp4": "confused_cat",
        "E141 旋转cheems.mov": "cat_rotating",
        "E22 摇摆猫.mp4": "cat_shaking_head_with_music",
        "E45 摇头猫.mp4": "cat_shaking_head_with_music",
        "E68 摇手猫.mp4": "cat_shaking_head_with_music",
        "E128 点头猫.mp4": "cat_shaking_head_with_music",
        "E72 点头OI猫.mp4": "cat_shaking_head_with_music",
        "E75 喝酒自拍猫.mp4": "cat_eating_snacks",
        "E138 健身喝酒猫.mov": "cat_eating_snacks",
        "E136 吃西瓜猫.mov": "cat_eating_a_cucumber",
        "E59 吃菜猫.mp4": "cat_eating_snacks",
        "E53 吃猫粮猫.mp4": "cat_eating_snacks",
        "E55 馋嘴奶猫.mp4": "cat_eating_snacks",
        "E79 干嚼猫.mp4": "cat_eating_snacks",
        "E80 吃火锅猫.mp4": "cat_eating_snacks",
        "E78 抱苹果猫.mp4": "cat_eating_snacks",
        "E53 敲碗猫.mp4": "cat_knocking_a_bowl",
        "E73 敲击猫.mp4": "cat_knocking_a_bowl",
        "E61 闭眼享受猫.mp4": "cat_eating_snacks",
        "E77 胖肚子猫.mp4": "fat_cat_dancing_with_music",
        "E133 腹肌猫.mp4": "fat_cat_dancing_with_music",
        "E131 收腹猫.mov": "fat_cat_dancing_with_music",
        "E130 开猫.mp4": "happy_cat_dancing",
        "E140  飞扑猫.mov": "happy_cat_dancing",
        "E143 举手下降猫.mov": "happy_cat_dancing",
        "E110 预备猫.mp4": "happy_cat_dancing",
        "E129 duangduang猫.mov": "happy_cat_dancing",
        "E129 duangduang猫 - 副本.mov": "happy_cat_dancing",
        "E135 爬行猫.mov": "cat_sitting",
        "E18 爬爬猫.mp4": "cat_sitting",
        "E132 踮脚猫.mov": "cat_sitting",
        "E134 摇摇椅猫.mov": "cat_sitting",
        "E133 睡袍猫.mov": "sleepy_cat",
        "E142 拿钱猫.mov": "cat_carrying_a_bag",
        "E13 数钱猫.mp4": "cat_carrying_a_bag",
        "E145 闻东西猫.mov": "cat_questioning",
        "E12 闻脚猫.mp4": "cat_questioning",
        "E127 侧脸猫.mp4": "cat_sitting",
        "E108 背影猫.mp4": "cat_sitting",
        "E23 背影摇摇猫.mp4": "cat_shaking_head_with_music",
        "E91 多个背影猫.mp4": "cat_sitting",
        "E109 自拍视角猫.mp4": "cat_sitting",
        "E5 自拍猫.mp4": "cat_sitting",
        "E88 端庄猫.mp4": "cat_sitting",
        "E89 倚靠猫.mp4": "cat_sitting",
        "E120 摸头猫.mp4": "cat_kissing_you",
        "F14 按摩猫.mp4": "F1_comfort_cat",
        "F15 一群水豚.mp4": "F1_comfort_cat",
        "F16 亲狗狗猫.mp4": "cat_kissing_you",
        "F17 舌吻猫.mp4": "cat_kissing_you",
        "F18 抱抱猫.mp4": "F12_hug_neck_cat",
        "F19 拥抱猫2.mp4": "F12_hug_neck_cat",
        "F2 死也要在一起.mp4": "F12_hug_neck_cat",
        "F20 围观猫.mp4": "cat_gazing_at_another_cat",
        "F22 盯着睡觉猫.mp4": "cat_gazing_at_another_cat",
        "F23 亲亲猫.mp4": "cat_kissing_you",
        "F24 抱抱猫.mp4": "F12_hug_neck_cat",
        "F26 抱着睡猫.mp4": "F12_hug_neck_cat",
        "F3 两小无猜猫.mp4": "F11_nuzzle_cat",
        "F4 亲热猫猫.mp4": "cat_kissing_you",
        "F5 亲脖子猫.mp4": "F13_kiss_head_cat",
        "F6 色诱猫.mp4": "cat_kissing_you",
        "F7 逛街猫.mp4": "cat_carrying_a_bag",
        "F8 两个背影猫.mp4": "F10_sync_head_shake_cats",
        "F9 亲亲猫猫头.mp4": "F13_kiss_head_cat",
        "E17 玩手机猫.mp4": "cat_working_on_the_computer",
        "E34 捂嘴看手机猫.mp4": "cat_working_on_the_computer",
        "E35 打电话猫.mp4": "cat_working_on_the_computer",
        "E39 玩手机猫.mp4": "cat_working_on_the_computer",
        "E56 玩手机猫.mp4": "cat_working_on_the_computer",
        "E92 玩手机猫.mp4": "cat_working_on_the_computer",
        "E112 打电话猫.mp4": "cat_working_on_the_computer",
        "E115 看手机猫.mp4": "cat_working_on_the_computer",
        "E11 照镜子猫.mp4": "cat_working_on_the_computer",
        "E19 按摩猫.mp4": "E101_massage_cat",
        "E70 按摩猫.mp4": "E101_massage_cat",
        "E16 等待猫.mp4": "cat_sitting",
        "E28 双手小猫.mp4": "cat_sitting",
        "E38 趴桌猫.mp4": "cat_sitting",
        "E64 躺着起来猫.mp4": "cat_sitting",
        "E63 逃走小猫.mp4": "cat_sitting",
        "E62 剪头猫.mp4": "cat_sitting",
        "E65 做卫生猫.mp4": "E1_washing_clothes_cat",
        "E54 洗衣服猫.mp4": "E1_washing_clothes_cat",
        "E119 洗碗猫.mp4": "E1_washing_clothes_cat",
        "E24 擦玻璃猫.mp4": "E1_washing_clothes_cat",
        "E51 擦玻璃猫.mp4": "E1_washing_clothes_cat",
        "E74 擦桌子猫.mp4": "E1_washing_clothes_cat",
        "E36 炒菜猫.mp4": "E1_washing_clothes_cat",
        "E81 织毛衣猫.mp4": "E1_washing_clothes_cat",
        "E3 踩缝纫机猫.mp4": "cat_working_on_the_computer",
        "E4 扣屁股小猫.mp4": "muddled_cat",
        "E2 拉屎猫.mp4": "muddled_cat",
        "E41 拉屎猫.mp4": "muddled_cat",
        "E27 呕吐猫 .mp4": "muddled_cat",
        "E52 咬东西猫.mp4": "A3_bite_things_cat",
        "E37 警车猫.mp4": "cat_driving_a_car",
        "B26 hum猫.mov": "singing_strange_cat",
        "B27 老吴猫.mov": "serious_cat_questioning",
        "B28 冻干哥.mov": "muddled_cat",
        "B29 希特勒猫.mp4": "angry_cat",
        "B30 希特勒邪恶猫.mp4": "angry_cat"
    }
    
    return mapping

def get_asset_id_from_filename(filename, mapping):
    """根据文件名获取对应的asset_id"""
    if filename in mapping:
        return mapping[filename]
    
    # 如果没有直接映射，尝试模糊匹配
    base_name = os.path.splitext(filename)[0]
    for mapped_name, asset_id in mapping.items():
        mapped_base = os.path.splitext(mapped_name)[0]
        if base_name.lower() in mapped_base.lower() or mapped_base.lower() in base_name.lower():
            return asset_id
    
    # 如果还是没有找到，生成一个基于文件名的ID
    # 确保正确处理中文字符编码
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
    clean_name = ''.join(clean_chars).lower()
    # 清理连续的下划线
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    return clean_name

def update_detail_json_with_mapping(detail_path, mapping, source_dir):
    """更新detail.json文件，添加映射的素材"""
    # 读取现有的detail.json
    with open(detail_path, 'r', encoding='utf-8') as f:
        detail_data = json.load(f)
    
    # 创建现有ID的集合
    existing_ids = {item['id'] for item in detail_data}
    
    # 遍历源目录中的所有视频文件
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                asset_id = get_asset_id_from_filename(file, mapping)
                
                # 如果这个ID还不存在，添加到detail.json
                if asset_id not in existing_ids:
                    # 根据文件名推断用途
                    usage = infer_usage_from_filename(file)
                    
                    detail_data.append({
                        "id": asset_id,
                        "usage": usage
                    })
                    existing_ids.add(asset_id)
                    print(f"添加新素材: {asset_id} - {usage}")
    
    # 保存更新后的detail.json
    with open(detail_path, 'w', encoding='utf-8') as f:
        json.dump(detail_data, f, ensure_ascii=False, indent=2)
    
    print(f"detail.json已更新，共有 {len(detail_data)} 个素材")

def infer_usage_from_filename(filename):
    """根据文件名推断素材用途"""
    name = filename.lower()
    
    if '吃' in name or '喝' in name or '咬' in name or '咀嚼' in name:
        return "吃东西，享受美食的场景"
    elif '对视' in name or '对话' in name or '打架' in name or '拳击' in name:
        return "对话交流，冲突争执的场景"
    elif '电脑' in name or '学习' in name or '工作' in name or '写字' in name:
        return "工作学习，专注思考的场景"
    elif '开车' in name or '骑' in name or '驾驶' in name:
        return "出行驾驶，移动交通的场景"
    elif '睡觉' in name or '困' in name or '哈欠' in name:
        return "疲惫困倦，休息放松的场景"
    elif '生气' in name or '愤怒' in name or '崩溃' in name:
        return "愤怒生气，情绪激动的场景"
    elif '开心' in name or '跳舞' in name or '庆祝' in name:
        return "开心愉悦，庆祝欢乐的场景"
    elif '亲' in name or '抱' in name or '爱' in name:
        return "亲密接触，表达爱意的场景"
    else:
        return "日常生活，各种场景"

if __name__ == "__main__":
    # 创建映射关系
    mapping = create_name_mapping()
    
    # 更新detail.json
    detail_path = "./memes/detail.json"
    source_dir = "./memes/猫meme小剧场"
    
    update_detail_json_with_mapping(detail_path, mapping, source_dir)