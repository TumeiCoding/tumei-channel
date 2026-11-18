# 土妹频道 · 资料库

土妹频道视频里用到的资料都放在这里：讲解演示（HTML 幻灯片）、PPT、思维导图，还有部分视频素材。内容有 AI 与编程，也有书籍讲解、音乐 MV 和生活感悟。

## 👉 在线浏览：https://tumeicoding.github.io/tumei-channel/

所有 HTML 演示都可以在上面这个页面里直接点开，支持搜索和按分类筛选，不用下载。

## 📂 目录结构

```
.
├── 书籍讲解/            # 每期视频一个文件夹，例如 261117-佛学的核心/
├── 音乐MV/
├── 生活感悟/
├── …                    # 新的分类直接建一个文件夹就行
├── Before2026/          # 2020–2025 年的旧资料（AI/大模型、编程、网络安全、区块链、个人成长）
├── index.html           # 在线浏览首页（自动生成，不用手改）
└── scripts/             # 生成 index.html 的脚本
```

旧资料的完整清单见 [Before2026/README.md](Before2026/README.md)。

## ➕ 怎么放新资料

1. 在对应分类下建一个文件夹，名字用 `YYMMDD-标题` 的格式，比如 `书籍讲解/261117-佛学的核心/`。日期会自动显示在首页上。
2. 把 HTML 演示、PPT、PDF、思维导图放进去。打包好的演示（文件夹里有 `index.html` 和 `assets/`）整个文件夹放进去就行，首页会把它当成一份演示。
3. 推送到 GitHub 以后，GitHub Actions 会自动更新首页 `index.html`，大约一两分钟后就能在线看到。

想在本地先看效果，可以在仓库根目录运行：

```bash
python3 scripts/build_index.py
```

## 📺 关注土妹频道

- YouTube：https://www.youtube.com/channel/UCu1lb_YUHcJFoc7lraETxvQ/
- B 站：https://space.bilibili.com/555585221/
- 西瓜视频：https://www.ixigua.com/home/2541718247050175
- 今日头条：https://profile.zjurl.cn/rogue/ugc/profile/?user_id=2541718247050175
