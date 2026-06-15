import csv
import sys

def is_valid_row(row):
    """
    检查一行 CSV 是否有效
    - 前 3 列是 基础信息（姓名、班级、学号等）
    - 后面每 3 列是一组服务（服务名, 分数, 时间）
    """
    if len(row) < 3:
        return False
    extra_cols = len(row) - 3
    if extra_cols % 3 != 0:
        return False
    return True

def check_csv(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader, start=1):
            if not is_valid_row(row):
                print(f"格式错误 - 第 {idx} 行: {row}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_csv.py 文件名.csv")
    else:
        check_csv(sys.argv[1])
