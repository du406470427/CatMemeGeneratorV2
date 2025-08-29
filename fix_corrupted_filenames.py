#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复乱码的PNG文件名
将编码错误的文件名恢复为正确的中文名称
"""

import os
import re
import shutil
from pathlib import Path

def fix_filename_encoding(corrupted_name):
    """
    尝试修复乱码的文件名
    """
    try:
        # 尝试将乱码字符串用latin-1解码，然后用utf-8编码
        fixed_name = corrupted_name.encode('latin-1').decode('utf-8')
        return fixed_name
    except (UnicodeDecodeError, UnicodeEncodeError):
        try:
            # 尝试其他编码方式
            fixed_name = corrupted_name.encode('cp1252').decode('utf-8')
            return fixed_name
        except (UnicodeDecodeError, UnicodeEncodeError):
            return None

def get_correct_directory_name(corrupted_dir):
    """
    根据乱码目录名推断正确的目录名
    """
    # 已知的映射关系
    known_mappings = {
        'g101_濮斿眻鐚': 'g101_委屈猫',
        'g102_鎰熷姩鐚': 'g102_感动猫',
        'g104_闇囨儕榛戠尗': 'g104_震惊黑猫',
        'g107_榛戣劯鐙': 'g107_黑脸狗',
        'g108_鐤戞儜鐚': 'g108_疑惑猫',
        'g109_澶х瑧绉冨ご鐚': 'g109_大笑秃头猫',
        'g10_閭呭獨涓€绗戠尗': 'g10_邪魅一笑猫',
        'g110_鎲ㄧ瑧鐙': 'g110_憨笑狗',
        'g111_榫囩墮鐙': 'g111_龇牙狗',
        'g113_鐤戞儜': 'g113_疑惑',
        'g115_鐢╁姩棣欒晧鐚': 'g115_甩动香蕉猫',
        'g116_鐥炶€佹澘': 'g116_痞老板',
        'g117_鐪眰鐚': 'g117_眯眼猫',
        'g118_璁ら敊鐚': 'g118_认错猫',
        'g119_涓嶅睉鐚': 'g119_不屑猫',
        'g11_濮斿眻鐚': 'g11_委屈猫',
        'g120_灏栧彨鐚': 'g120_尖叫猫',
        'g12_鍙戠幇鐚': 'g12_发现猫',
        'g133_鍛嗘粸鐚': 'g133_呆滞猫',
        'g137_鐢熸皵鐚': 'g137_生气猫',
        'g138_鏂滅溂鐚': 'g138_斜眼猫',
        'g139__闇囨儕棣欒晧鐚': 'g139__震惊香蕉猫',
        'g13_鏁查攨鐙楀瓙': 'g13_敲锅狗子',
        'g141_涓炬墜棣欒晧鐚': 'g141_举手香蕉猫',
        'g143_澶ц€虫湹濮斿眻鐚': 'g143_大耳朵委屈猫',
        'g144_鎼炵瑧榧': 'g144_搞笑鼠',
        'g145_鏈ㄥ槦鍢ㄧ尗': 'g145_木嘿嘿猫',
        'g146_鏈夌悊璇翠笉娓呯尗': 'g146_有理说不清猫',
        'g148_闇囨儕楸肩溂': 'g148_震惊鱼眼',
        'g14_鏁查キ鐩嗙尗': 'g14_敲饭盆猫',
        'g150_濮斿眻鐚': 'g150_委屈猫',
        'g151_鐤戞儜鐙': 'g151_疑惑狗',
        'g15_鍚冩儕鐚': 'g15_吃惊猫',
        'g16_澶х瑧鐚': 'g16_大笑猫',
        'g17_濮斿眻鐚': 'g17_委屈猫',
        'g18_鍌荤瑧鐚': 'g18_傻笑猫',
        'g19_鎮蹭激鐙': 'g19_悲伤狗',
        'g1_瀵硅瘽鐚': 'g1_对话猫',
        'g20_鎹傚槾绗戠尗': 'g20_捂嘴笑猫',
        'g21_寰瑧鐚': 'g21_微笑猫',
        'g22_杩风硦鐚': 'g22_迷糊猫',
        'g23_鍌荤瑧鐙': 'g23_傻笑狗',
        'g24_闇囨儕鐚': 'g24_震惊猫',
        'g25_鍛嗘粸鐚': 'g25_呆滞猫',
        'g27_鍦伴搧鑰佷汉鐚': 'g27_地铁老人猫',
        'g28_寰堝嚩鐚': 'g28_很凶猫',
        'g2_huh鎵嬫Υ寮': 'g2_huh手榴弹',
        'g31_璁ゆ€傜尗': 'g31_认怂猫',
        'g32_鐥村憜鐚': 'g32_痴呆猫',
        'g33_澶х瑧鐚': 'g33_大笑猫',
        'g34_鎮蹭激灏忕尗': 'g34_悲伤小猫',
        'g35_鎶卞ご鐚': 'g35_抱头猫',
        'g36_鍐烽潤澶х溂鐚': 'g36_冷静大眼猫',
        'g37_鍦熸嫧榧犲皷鍙玙': 'g37_土拨鼠尖叫_',
        'g38_棰ゆ姈鐗欓娇鎵撴灦鐙': 'g38_颤抖牙齿打架狗',
        'g3_鐖嗙瑧鐚': 'g3_爆笑猫',
        'g41_缈荤櫧鐪肩尗_': 'g41_翻白眼猫_',
        'g42_澶х瑧鐙梍': 'g42_大笑狗_',
        'g43_瀹虫€曠尗': 'g43_害怕猫',
        'g47_榛戠尗灏栧彨': 'g47_黑猫尖叫',
        'g48_瀚屽純鐚': 'g48_嫌弃猫',
        'g49_闇囨儕鐚': 'g49_震惊猫',
        'g4_闇囨儕鐚': 'g4_震惊猫',
        'g50_鍝€鍡界尗': 'g50_哀嚎猫',
        'g51_姝ゅご鍙埍鐚': 'g51_歪头可爱猫',
        'g52_濮斿眻鐚': 'g52_委屈猫',
        'g53_涓嶅睉鐚': 'g53_不屑猫',
        'g53_鐬ぇ鐪肩尗': 'g53_瞪大眼猫',
        'g55_鐪兼唱姹按鐚': 'g55_眼泪汪汪猫',
        'g56_寰楅€炵尗': 'g56_得逞猫',
        'g58_鐧荤瑧鐚': 'g58_癫笑猫',
        'g59_涓嶈€愮儲鐚': 'g59_不耐烦猫',
        'g5_鎰ゆ€掔尗': 'g5_愤怒猫',
        'g60_宕╂簝鐚': 'g60_崩溃猫',
        'g62_闇囨儕鍛嗙尗': 'g62_震惊呆猫',
        'g66_鎰忓懗娣遍暱鐚': 'g66_意味深长猫',
        'g68_閿€榄傜尗': 'g68_销魂猫',
        'g69_澶ц劯鐗瑰啓鐚': 'g69_大脸特写猫',
        'g6_灏栧彨榧': 'g6_尖叫鼠',
        'g70_闇囨儕鐚': 'g70_震惊猫',
        'g71_鐩潃鐚': 'g71_盯着猫',
        'g72_瀹虫€曠尗': 'g72_害怕猫',
        'g74_濮斿眻鐚': 'g74_委屈猫',
        'g76_宕╂簝澶у彨鐚': 'g76_崩溃大叫猫',
        'g78_鍙嶉棶鐚': 'g78_反问猫',
        'g79_鏃犺緶鐚': 'g79_无辜猫',
        'g80_鍐诲共鍝': 'g80_冻干哥',
        'g81_棣欒晧鐚蛋_鍝': 'g81_香蕉猫走_哭',
        'g82_闇囨儕鐚': 'g82_震惊猫',
        'g83_绾㈡俯绗': 'g83_红温笑',
        'g84_鏂伴矞鍝': 'g84_新鲜哥',
        'g85_濮斿眻鐚': 'g85_委屈猫',
        'g86_鐧界溂鐚': 'g86_白眼猫',
        'g87_鎳电尗': 'g87_懵猫',
        'g88_澶у彨鐚': 'g88_大叫猫',
        'g89_娓╂煍鐚': 'g89_温柔猫',
        'g8_鍙堟€曞張瑕佸悆': 'g8_又怕又要吃',
        'g90_鍥炲簲鐚': 'g90_回应猫',
        'g91_濂哥瑧鐚': 'g91_奸笑猫',
        'g92_鏃犺緶鐚': 'g92_无辜猫',
        'g93_娌夋€濈尗': 'g93_沉思猫',
        'g94_鐢熸皵鐚': 'g94_生气猫',
        'g95_鐢熸皵鐙': 'g95_生气狗',
        'g99_寮€蹇冪嫍': 'g99_开心狗',
        'g9_瀹崇緸鐚': 'g9_害羞猫',
        'h10_鑷嚟鐚玙': 'h10_臭猫_',
        'h11_韫﹁开鐙': 'h11_蹦迪狗',
        'h12_鎵姩鑰侀紶': 'h12_扭动老鼠',
        'h13_绉戠洰涓夎烦鑸炵尗': 'h13_科目三跳舞猫',
        'h14_钃濆附瀛愯烦鑸炵尗_': 'h14_蓝帽子跳舞猫_',
        'h15_澧ㄩ暅鎵撶鐚玙': 'h15_墨镜打碟猫_',
        'h17_鎽╂墭鑸炵尗': 'h17_摩托舞猫',
        'h18_鍚変粬鐚': 'h18_吉他猫',
        'h19_瀵圭潃璇濈瓛鍞辨瓕': 'h19_对着话筒唱歌',
        'h1_鍑虹敓榧犻紶': 'h1_出生鼠鼠',
        'h20_浜旀潯鎮熺尗': 'h20_五条悟猫',
        'h21_happy鐚': 'h21_happy猫',
        'h22_澶т浆鐚': 'h22_大佬猫',
        'h23_婕斿敱浼氱粍鍚堢尗': 'h23_演唱会组合猫',
        'h24_鍚嶅獩璺宠垶鐚': 'h24_名媛跳舞猫',
        'h25_鎿︾幓鐠冪尗': 'h25_擦玻璃猫',
        'h26_鎿︾幓鐠冮粦鐚': 'h26_擦玻璃黑猫',
        'h27_琛ㄦ紨鐚': 'h27_表演猫',
        'h28_铚滆渹鐚': 'h28_蜜蜂猫',
        'h29_鍞辨瓕鐚': 'h29_唱歌猫',
        'h30_鍞辨瓕鐚': 'h30_唱歌猫',
        'h31_鏃嬭浆鐚': 'h31_旋转猫',
        'h32_鍙戣█鐚': 'h32_发言猫',
        'h33_璇濈瓛鐚': 'h33_话筒猫',
        'h35_鍚瑰彿瀛愮尗': 'h35_吹号子猫',
        'h36_寮归挗鐞寸尗': 'h36_弹钢琴猫',
        'h37_璺宠垶鐚': 'h37_跳舞猫',
        'h38_鍒虹尗璺宠垶': 'h38_刺猬跳舞',
        'h39_鍙樿壊鑴哥尗': 'h39_变色脸猫',
        'h3_chipi鐚玙': 'h3_chipi猫_',
        'h40_鏈哄櫒鐙': 'h40_机器狗',
        'h41_鍢诲搱鐙': 'h41_嘻哈狗',
        'h4_happy鐚': 'h4_happy猫',
        'h5_璺宠垶鐚玙': 'h5_跳舞猫_',
        'h6_绾㈤┈鐢茶烦鑸炵尗': 'h6_红马甲跳舞猫',
        'h7_绉戠洰涓夎烦鑸炵尗': 'h7_科目三跳舞猫',
        'h8_璺宠垶鐚玙': 'h8_跳舞猫_',
        'h9_51121鐚': 'h9_51121猫',
        'i10_槌嫓鐚': 'i10_鳌拜猫',
        'i11_鏂滃垬娴风尗_': 'i11_斜刘海猫_',
        'i123_鍏槑鐙': 'i123_八嘎狗',
        'i12_璐靛鐚': 'i12_贵妇猫',
        'i13_纾ㄦ寚鐢茬尗': 'i13_磨指甲猫',
        'i14_绮夊ご鍙戠嫍': 'i14_粉头发狗',
        'i15_rap鐚': 'i15_rap猫',
        'i16_鎴寸溂闀滅尗': 'i16_戴眼镜猫',
        'i17_鍚嶅獩鐚': 'i17_名媛猫',
        'i18_鍦ｅ儳鐚': 'i18_圣僧猫',
        'i19_缇庡コ鐚': 'i19_美女猫',
        'i1_涓炬墜鐚': 'i1_举手猫',
        'i20_鐪奸暅鐚': 'i20_眼镜猫',
        'i21_澶у鐙': 'i21_大妈狗',
        'i22_缇庡コ鐚': 'i22_美女猫',
        'i24_鍖荤敓鐚': 'i24_医生猫',
        'i2__閫€涓嬬尗': 'i2__退下猫',
        'i3_鎽樼溂闀滅尗': 'i3_摘眼镜猫',
        'i4_鏃ョ郴缇庡コ鐚': 'i4_日系美女猫',
        'i5_鐩涜鐚': 'i5_盛装猫',
        'i6_榫呯墮鐚': 'i6_龅牙猫',
        'i7_鏈夐挶鐚': 'i7_有钱猫',
        'i8_鐭ユ€х編鐚': 'i8_知性美猫',
        'i9_鎬昏鐚': 'i9_总裁猫',
        # 新发现的乱码映射
        'g117_鐪溂鐚': 'g117_眯眼猫',
        'g21_寰瑧鐚': 'g21_微笑猫',
        'g51_姝ご鍙埍鐚': 'g51_歪头可爱猫',
        'g55_鐪兼唱姹豹鐚': 'g55_眼泪汪汪猫',
        'g58_鐧瑧鐚': 'g58_癫笑猫',
        'g81_棣欒晧鐚蛋_鍝璡': 'g81_香蕉猫走_哭',
        'i123_鍏槑鐙梊': 'i123_八嘎狗',
        'i21_澶у鐙梊': 'i21_大妈狗'
    }
    
    # 首先检查已知映射
    for corrupted, correct in known_mappings.items():
        if corrupted in corrupted_dir:
            return correct
    
    # 尝试自动修复编码
    fixed = fix_filename_encoding(corrupted_dir)
    if fixed:
        return fixed
    
    return None

def main():
    memes_dir = Path('./memes')
    
    if not memes_dir.exists():
        print("memes目录不存在")
        return
    
    # 统计乱码文件 - 只查找直接在memes目录下的PNG文件
    corrupted_files = []
    
    for png_file in memes_dir.glob('*.png'):
        filename = png_file.name
        # 检查是否包含乱码字符
        if re.search(r'[鍏槑鐙梊濮斿眻鎰熷姩闇囨儕榛戣劯鐤戞儜澶х瑧绉冨ご閭呭獨涓€绗戞憨榫囩墮鐢╁姩棣欒晧鐥炶€佹澘鐪眰璁ら敊涓嶅睉灏栧彨鍙戠幇鍛嗘粸]', filename):
            corrupted_files.append(png_file)
    
    print(f"发现 {len(corrupted_files)} 个乱码PNG文件")
    
    if not corrupted_files:
        print("没有发现乱码文件")
        return
    
    # 按文件名前缀分组（提取asset_id）
    asset_groups = {}
    for file_path in corrupted_files:
        filename = file_path.name
        # 提取asset_id（文件名中帧号之前的部分，去掉可能的乱码后缀如'玕'）
        match = re.match(r'(.+?)(?:玕)?\d{4}\.png$', filename)
        if match:
            asset_id = match.group(1)
            if asset_id not in asset_groups:
                asset_groups[asset_id] = []
            asset_groups[asset_id].append(file_path)
    
    print(f"涉及 {len(asset_groups)} 个素材")
    
    # 处理每个素材
    fixed_count = 0
    for corrupted_asset_id, files in asset_groups.items():
        print(f"\n处理素材: {corrupted_asset_id}")
        
        # 获取正确的asset_id
        correct_asset_id = get_correct_directory_name(corrupted_asset_id)
        
        if not correct_asset_id:
            print(f"  无法确定正确的素材ID，跳过")
            continue
        
        print(f"  正确素材ID: {correct_asset_id}")
        
        # 检查正确的目录是否已存在
        correct_dir_path = memes_dir / correct_asset_id
        
        if not correct_dir_path.exists():
            correct_dir_path.mkdir(exist_ok=True)
            print(f"  创建目录: {correct_dir_path}")
        
        # 移动PNG文件到正确目录
        for file_path in files:
            frame_match = re.search(r'(\d{4})\.png$', file_path.name)
            if frame_match:
                new_filename = f"{frame_match.group(1)}.png"
                new_path = correct_dir_path / new_filename
                
                try:
                    shutil.move(str(file_path), str(new_path))
                    print(f"    移动: {file_path.name} -> {new_path}")
                    fixed_count += 1
                except Exception as e:
                    print(f"    移动失败: {e}")
    
    print(f"\n修复完成，共处理 {fixed_count} 个文件")

if __name__ == '__main__':
    main()