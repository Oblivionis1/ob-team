import os
import re

def fix_relative_imports():
    """修复所有Python文件中的相对导入问题"""
    # 要处理的目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        os.path.join(base_dir, "app", "routes"),
        os.path.join(base_dir, "app", "models")
    ]
    
    # 要替换的模式和替换内容
    replacements = [
        (r"from \.\.\.database import", "from database import"),
        (r"from \.\.\.input_processor import", "from input_processor import"),
        (r"from \.\.\.question_generator import", "from question_generator import"),
        (r"from \.\.config import", "from config import"),
        (r"from \.\.database import", "from database import"),
        (r"from \.\.input_processor import", "from input_processor import"),
        (r"from \.\.question_generator import", "from question_generator import"),
    ]
    
    # 遍历所有目录
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                filepath = os.path.join(directory, filename)
                print(f"检查文件: {filepath}")
                
                # 读取文件内容
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 执行所有替换
                new_content = content
                for pattern, replacement in replacements:
                    new_content = re.sub(pattern, replacement, new_content)
                
                # 如果内容发生变化，保存回文件
                if new_content != content:
                    print(f"修复文件: {filepath}")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)

if __name__ == "__main__":
    fix_relative_imports()
    print("导入问题修复完成!") 