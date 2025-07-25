# PQ 系统

PQ 系统是一个综合性解决方案，用于从教育内容生成测验题目。它支持处理文本、PowerPoint、PDF、音频和视频输入，自动提取内容并为教育用途生成多项选择题。

## 功能特点

1. **输入处理**
   - 文本文件处理
   - PowerPoint 文件处理
   - PDF 文件处理
   - 音频文件处理
   - 视频文件处理（包含音频转录和视觉文本提取）

2. **题目生成**
   - AI 驱动的多项选择题生成
   - 质量检查与改进循环
   - 难度级别选择
   - 支持多种教育主题

3. **用户管理**
   - 三种用户角色：组织者、演示者和观众
   - 用户注册与认证
   - 基于角色的访问控制

4. **测验管理**
   - 从处理后的内容创建测验
   - 设置测验的开始和结束时间
   - 题目顺序随机化
   - 选项顺序随机化以防止简单抄袭

5. **反馈系统**
   - 题目质量反馈
   - 演示者反馈
   - 环境反馈
   - 每个题目的讨论区

6. **数据分析**
   - 面向演示者和组织者的测验统计
   - 面向观众的个人表现分析
   - 反馈分析工具

## 安装指南

### 先决条件

- Python 3.8+
- FFmpeg (用于音频/视频处理)
- Tesseract OCR (用于视频帧文本提取)

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/pq_system.git
cd pq_system
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Windows系统: venv\Scripts\activate
```

3. 安装依赖包：

```bash
pip install -r requirements.txt
```

4. 设置环境变量（在根目录创建 `.env` 文件）：

```
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

5. 初始化数据库：

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 使用说明

1. 启动应用：

```bash
python main.py --debug
```

2. 访问 Web 界面：
   - 打开浏览器访问 `http://localhost:5000`

3. 注册不同用户类型：
   - 组织者：创建和管理活动，监控测验
   - 演示者：上传内容，创建测验，查看结果
   - 观众：参加测验，提供反馈，参与讨论

4. 上传内容：
   - 以演示者身份登录
   - 导航到 内容 → 上传
   - 选择文件和内容类型
   - 提供标题和描述

5. 生成题目：
   - 查看已上传内容
   - 选择"生成题目"
   - 选择题目数量和难度

6. 创建测验：
   - 选择要包含的题目
   - 设置测验参数
   - 发布测验

7. 参加测验：
   - 以观众身份登录
   - 导航到可用测验
   - 回答问题并查看结果

## 项目结构

```
pq_system/
├── app/                       # Web 应用
│   ├── routes/                # API 路由
│   ├── models/                # 数据库模型
│   ├── static/                # 静态文件
│   └── templates/             # HTML 模板
├── input_processor/           # 输入处理模块
├── question_generator/        # 题目生成模块
├── config.py                  # 配置文件
├── database.py                # 数据库连接
└── main.py                    # 主应用入口
```

## 自定义选项

- **OpenAI 模型**：可在 `question_generator/generator.py` 中更改 OpenAI 模型，使用 GPT-4 等更高级模型以获得更好的题目质量
- **题目质量参数**：调整 `question_generator/quality_checker.py` 中的阈值以改变质量检查的严格程度
- **输入处理器**：通过修改 `input_processor` 目录中的模块扩展输入处理能力

## 贡献指南

欢迎贡献！请随时提交 Pull Request。

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。
