# Git 仓库迁移与推送 - 2026-01-31

## 任务
将 stock_stars 项目抹除旧 git 设置，重新初始化并推送到 GitHub 用户仓库。

## 思考过程
1. 删除项目中的 `.git` 目录（抹除旧设置）
2. 重新 `git init` 初始化
3. 配置 .gitignore 排除不需要的文件（venv, 数据文件等）
4. 尝试使用 `gh repo create` 推送到 GitHub
5. 遇到 auth 问题，需要用户先登录

## 行动步骤
1. 删除旧 git：`rm -rf .git`
2. 重新初始化：`git init`
3. 配置 .gitignore：
   - 排除 venv, data, log, reports
   - 排除 *.parquet, *.csv, *.png
4. 添加核心文件：
   - README.md, requirements.txt
   - trading-system/ 目录
   - api_test/, notebooks/
5. 首次提交：`git commit -m "Initial commit: stock trading system"`
6. 配置用户信息：
   ```bash
   git config user.name "Eric"
   git config user.email "ericymtx@icloud.com"
   ```
7. 尝试创建远程仓库：`gh repo create stock-star --public --source=. --push`
8. 遇到 auth 错误，需要用户先 `gh auth login`

## 待完成
- 用户运行 `gh auth login`
- 然后执行推送命令

## 注意事项
- 项目中有嵌套的 git submodule（anthropics-skills, extern/StockTradebyZ），需要排除
- 确保不包含敏感数据（日志、缓存、测试报告）
