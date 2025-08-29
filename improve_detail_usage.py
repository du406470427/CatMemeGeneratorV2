#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进detail.json中的usage描述
基于素材ID和内容特征，提供更具体和多样化的usage描述
"""

import json
import re
from pathlib import Path

def create_improved_usage_mapping():
    """创建改进的usage映射关系"""
    usage_mapping = {
        # A类 - 吃东西类
        "A1_drink_ad_calcium_cat": "喝饮料，补充营养的场景",
        "A10_eat_fish_snack_cat": "享用零食，品尝美味的场景", 
        "A2_eat_chips_cat": "吃薯片，休闲娱乐的场景",
        "A3_bite_things_cat": "咀嚼食物，专注进食的场景",
        "A5_chewing_cat": "细嚼慢咽，享受美食的场景",
        
        # B类 - 对话&打架类
        "B1_nervous_stare_cat": "紧张对视，心理博弈的场景",
        "B11_probe_cat": "试探观察，谨慎交流的场景",
        "B12_kick_cat": "激烈冲突，动作对抗的场景",
        "B13_boxing_cat": "拳击格斗，竞技比赛的场景",
        "B14_gun_cat": "武器对峙，紧张刺激的场景",
        "B15_big_tongue_donkey": "搞怪表情，幽默逗趣的场景",
        "B16_pop_cat": "突然出现，惊喜意外的场景",
        "B17_confused_dialogue": "疑惑交流，困惑不解的场景",
        "B18_punch_cat": "出拳攻击，激烈争斗的场景",
        "B19_quarrel_cat": "激烈争吵，情绪冲突的场景",
        "B2_hit_head_cat": "敲击头部，惩罚教训的场景",
        "B20_handsome_brother_cat": "帅气登场，魅力展示的场景",
        "singing_strange_cat": "奇特歌唱，音乐表演的场景",
        "serious_cat_questioning": "严肃质疑，认真询问的场景",
        "muddled_cat": "迷糊困惑，思维混乱的场景",
        "angry_cat": "愤怒暴躁，情绪爆发的场景",
        "cat_gazing_at_another_cat": "深情凝视，专注观察的场景",
        "a_cat_hitting_another_cat": "互相打斗，肢体冲突的场景",
        "cat_being_interviewed": "接受采访，回答问题的场景",
        
        # C类 - 工作&学习类
        "C1_computer_cat": "电脑办公，专业工作的场景",
        "C2_blue_shirt_computer_cat": "正装办公，商务工作的场景",
        "C3_computer_dog": "宠物办公，轻松工作的场景",
        "C4_writing_cat": "书写记录，文字创作的场景",
        "C5_customer_service_cat": "客户服务，沟通交流的场景",
        "C6_studying_cat": "认真学习，知识获取的场景",
        "C7_reading_newspaper_cat": "阅读新闻，信息获取的场景",
        "C8_reading_book_cat": "读书学习，知识积累的场景",
        
        # D类 - 骑车&驾驶类
        "D1_driving_cat": "驾车出行，交通工具的场景",
        "D2_motorcycle_cat": "摩托骑行，速度激情的场景",
        "D3_small_motorcycle_cat": "小型摩托，轻便出行的场景",
        "D4_sunglasses_driving": "酷炫驾驶，时尚出行的场景",
        "D5_beauty_cat_riding_donkey": "骑驴出行，传统交通的场景",
        "D6_mouse_cycling": "骑车运动，健康出行的场景",
        "D7_driving_cat_2": "汽车驾驶，现代出行的场景",
        
        # E类 - 生活行为类
        "E1_washing_clothes_cat": "洗衣做家务，生活劳动的场景",
        "E10_cape_cat": "披风造型，英雄气概的场景",
        "E100_smell_cat": "嗅闻气味，感官体验的场景",
        "E101_massage_cat": "按摩放松，身体护理的场景",
        "E102_bow_head_cat": "低头思考，沉思反省的场景",
        "E103_jumping_cat": "跳跃运动，活力四射的场景",
        "E104_walking_cat": "步行移动，日常行走的场景",
        "E105_look_around_cat": "环顾四周，观察环境的场景",
        
        # F类 - 情侣猫
        "F1_comfort_cat": "安慰关怀，温暖陪伴的场景",
        "F10_sync_head_shake_cats": "同步摆头，默契配合的场景",
        "F11_nuzzle_cat": "亲昵蹭蹭，温柔接触的场景",
        "F12_hug_neck_cat": "拥抱脖颈，深情拥抱的场景",
        "F13_kiss_head_cat": "亲吻头部，爱意表达的场景",
        
        # 特殊情感和行为类
        "cat_yawning": "打哈欠，疲惫困倦的场景",
        "cat_sitting": "静坐休息，安静等待的场景",
        "cat_working_on_the_computer": "电脑操作，数字化工作的场景",
        "happy_cat_dancing": "欢乐舞蹈，庆祝喜悦的场景",
        "cat_feeling_wronged": "委屈难过，情感受伤的场景",
        "cat_questioning": "疑问询问，寻求答案的场景",
        "cat_kissing_you": "亲吻互动，亲密表达的场景",
        "cat_rotating": "旋转运动，动态展示的场景",
        "confused_cat": "困惑迷茫，不知所措的场景",
        "cat_on_a_motor_rotating": "机械旋转，科技互动的场景",
        "sheep_sticking_out_tongue": "吐舌卖萌，可爱表情的场景",
        "cat_shaking_head_with_music": "音乐摇摆，节奏律动的场景",
        "cat_carrying_a_bag": "携带物品，出行准备的场景",
        "fat_cat_dancing_with_music": "胖猫舞蹈，自信展示的场景",
        "sleepy_cat": "昏昏欲睡，休息放松的场景",
        "cat_eating_a_cucumber": "品尝蔬菜，健康饮食的场景",
        "cat_eating_snacks": "享用零食，美食品尝的场景",
        "banana-like-cat-fainting": "香蕉猫晕倒，搞笑意外的场景",
        "wet_upset_cat": "湿漉沮丧，狼狈不堪的场景",
        "shocked_cat": "震惊惊讶，意外反应的场景",
        "cat_rapidly_opening_and_closing_mouth": "快速说话，激动表达的场景",
        "crying_banana-like-cat": "哭泣伤心，情感宣泄的场景",
        "curl_up_cat_shaking": "蜷缩颤抖，恐惧害怕的场景",
        "cat_driving_a_car": "开车驾驶，交通出行的场景",
        "hopeless_cat": "绝望无助，情绪低落的场景",
        "cat_knocking_a_bowl": "敲击碗具，催促要求的场景",
        "cat_dressing_in_chinese_new_year_style_dancing": "新年舞蹈，节日庆祝的场景",
        "cat_making_a_bow": "鞠躬致敬，礼貌表达的场景",
        "cat_holding_head_and_screaming": "抱头尖叫，崩溃绝望的场景",
        "shouting_cat": "大声呼喊，情绪激动的场景"
    }
    
    return usage_mapping

def improve_detail_json_usage(detail_path):
    """改进detail.json中的usage描述"""
    # 读取现有的detail.json
    with open(detail_path, 'r', encoding='utf-8') as f:
        detail_data = json.load(f)
    
    # 获取改进的usage映射
    usage_mapping = create_improved_usage_mapping()
    
    # 更新每个素材的usage
    updated_count = 0
    for item in detail_data:
        asset_id = item['id']
        if asset_id in usage_mapping:
            old_usage = item['usage']
            new_usage = usage_mapping[asset_id]
            if old_usage != new_usage:
                item['usage'] = new_usage
                updated_count += 1
                print(f"更新 {asset_id}: {old_usage} -> {new_usage}")
        else:
            # 对于没有特定映射的ID，根据ID特征推断更具体的usage
            new_usage = infer_usage_from_id(asset_id)
            if new_usage != item['usage']:
                item['usage'] = new_usage
                updated_count += 1
                print(f"推断 {asset_id}: {item['usage']} -> {new_usage}")
    
    # 保存更新后的detail.json
    with open(detail_path, 'w', encoding='utf-8') as f:
        json.dump(detail_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n已更新 {updated_count} 个素材的usage描述")
    print(f"detail.json已保存，共有 {len(detail_data)} 个素材")

def infer_usage_from_id(asset_id):
    """根据asset_id推断更具体的usage"""
    id_lower = asset_id.lower()
    
    # 根据ID中的关键词推断用途
    if any(word in id_lower for word in ['eat', 'drink', 'bite', 'chew', '吃', '喝', '咬']):
        return "美食享用，进食品尝的场景"
    elif any(word in id_lower for word in ['sleep', 'yawn', 'tired', '睡', '困', '累']):
        return "休息睡眠，疲惫放松的场景"
    elif any(word in id_lower for word in ['angry', 'mad', 'rage', '怒', '气', '愤']):
        return "愤怒生气，情绪激动的场景"
    elif any(word in id_lower for word in ['happy', 'dance', 'joy', '乐', '开心', '跳']):
        return "欢乐愉悦，庆祝开心的场景"
    elif any(word in id_lower for word in ['love', 'kiss', 'hug', '爱', '亲', '抱']):
        return "亲密互动，爱意表达的场景"
    elif any(word in id_lower for word in ['work', 'computer', 'study', '工作', '电脑', '学习']):
        return "工作学习，专注思考的场景"
    elif any(word in id_lower for word in ['drive', 'car', 'motor', '开车', '驾驶', '车']):
        return "驾驶出行，交通工具的场景"
    elif any(word in id_lower for word in ['confused', 'question', 'wonder', '困惑', '疑问', '奇怪']):
        return "困惑疑问，思考探索的场景"
    elif any(word in id_lower for word in ['shock', 'surprise', 'amaze', '震惊', '惊讶', '意外']):
        return "震惊惊讶，意外反应的场景"
    elif any(word in id_lower for word in ['sad', 'cry', 'upset', '伤心', '哭', '难过']):
        return "伤心难过，情感低落的场景"
    elif any(word in id_lower for word in ['rotate', 'spin', 'turn', '旋转', '转', '摇']):
        return "旋转运动，动态展示的场景"
    elif any(word in id_lower for word in ['sit', 'wait', 'stand', '坐', '等', '站']):
        return "静态等待，安静休息的场景"
    else:
        return "日常行为，生活场景的展示"

if __name__ == "__main__":
    # 改进detail.json的usage描述
    detail_path = "./memes/detail.json"
    improve_detail_json_usage(detail_path)