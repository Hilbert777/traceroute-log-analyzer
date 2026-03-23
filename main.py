import glob
import re
import os
import math

def calculate_stats(rtt_values):
    if not rtt_values:
        return 0.0, 0.0
    
    n = len(rtt_values)
    mean = sum(rtt_values) / n
    
    if n > 1:
        variance = sum((x - mean) ** 2 for x in rtt_values) / (n - 1)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0.0
        
    return mean, std_dev

def get_file_number(filename):
    # 提取文件名中的数字用于排序 log1.txt -> 1
    match = re.search(r'(\d+)', os.path.basename(filename))
    if match:
        return int(match.group(1))
    return 0

def parse_logs():
    # 获取当前目录下所有的 log*.txt 文件
    log_file_list = glob.glob('log*.txt')
    
    # 按文件名中的数字排序
    log_file_list.sort(key=get_file_number)
    
    final_results = []

    for log_path in log_file_list:
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {log_path}: {e}")
            continue
            
        current_target = None
        current_rtt_values = []
        is_processing = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是新的 traceroute 命令开始
            # 兼容 "traceroute to <target> ..."
            target_match = re.search(r'traceroute to (\S+) \(', line)
            
            if target_match:
                # 如果之前正在处理一个目标，先结算保存
                if is_processing and current_target:
                    mean_val, std_dev_val = calculate_stats(current_rtt_values)
                    # 格式化输出为一行
                    final_results.append((os.path.basename(log_path), current_target, mean_val, std_dev_val))
                
                # 开始新记录
                current_target = target_match.group(1)
                current_rtt_values = []
                is_processing = True
                continue
            
            # 如果没有在处理目标，跳过
            if not is_processing:
                continue
            
            # 提取 ms 值，忽略 '*'
            # 匹配整数或小数，后面紧跟 " ms"
            ms_matches = re.findall(r'(\d+(?:\.\d+)?) ms', line)
            for val in ms_matches:
                current_rtt_values.append(float(val))

        # 文件结束时，如果在处理中，结算最后一条记录
        if is_processing and current_target:
            mean_val, std_dev_val = calculate_stats(current_rtt_values)
            final_results.append((os.path.basename(log_path), current_target, mean_val, std_dev_val))

    # 写入结果到 result.txt
    try:
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write(f"{'Filename':<15} {'Target':<20} {'Mean (ms)':<10} {'StdDev (ms)':<10}\n")
            f.write("-" * 60 + "\n")
            for fname, target, mean, std in final_results:
                f.write(f"{fname:<15} {target:<20} {mean:<10.2f} {std:<10.2f}\n")
        
        print("处理完成! 结果已写入 result.txt")
        print("-" * 60)
        print(f"{'Filename':<15} {'Target':<20} {'Mean (ms)':<10} {'StdDev (ms)':<10}")
        for fname, target, mean, std in final_results:
            print(f"{fname:<15} {target:<20} {mean:<10.2f} {std:<10.2f}")
            
    except Exception as e:
        print(f"Error writing result.txt: {e}")

if __name__ == "__main__":
    parse_logs()
