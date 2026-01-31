#!/bin/bash

# 設定 repo 路徑
REPO_DIR=/Users/henry.lee/HENRY/tools
cd "$REPO_DIR" || exit

# 拉最新變更，避免衝突
git pull origin main

# 加所有檔案（.gitignore 會自動排除不需要的檔案）
git add .

# 只有有變更才 commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit"
    exit 0
fi

# 自動 commit，附上日期時間
git commit -m "Auto commit $(date '+%Y-%m-%d %H:%M:%S')"

# 推到 GitHub
git push origin main
