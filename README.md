# jiqiren — 机器人联盟官网

机器人最前沿 · 基于 **Hugo** 与 **universal 主题** 的企业官网，托管于 **GitHub Pages**，域名 `jiqiren.gs.cn`。

## 技术栈

- [Hugo](https://gohugo.io)（extended）静态站点框架
- 主题：[hugo-universal-theme](https://github.com/devcows/hugo-universal-theme)（git submodule）
- 部署：GitHub Actions 自动构建并发布到 GitHub Pages
- 多语言：中文（默认，站根路径）/ English（`/en/`）

## 目录结构

```
.
├── hugo.toml            # 站点配置（多语言、菜单、首页板块参数）
├── content/
│   ├── zh/              # 中文内容（默认语言）
│   │   ├── about.md     # 关于我们
│   │   ├── products/    # 产品中心（_index.md + 各产品页）
│   │   ├── contact.md   # 联系我们
│   │   ├── faq.md       # 常见问题
│   │   └── blog/        # 新闻动态
│   └── en/              # English 内容
├── data/                # 首页数据（轮播/服务/客户评价/合作客户）
├── static/
│   ├── CNAME            # 自定义域名
│   └── img/             # 站点图片（Logo、轮播图等）
├── i18n/                # 语言翻译覆盖
├── themes/
│   └── hugo-universal-theme/   # 主题（submodule）
└── .github/workflows/hugo.yaml # 自动部署工作流
```

## 本地开发

```bash
# 安装 Hugo extended 后：
hugo server -D          # 本地预览 http://localhost:1313
hugo                    # 构建到 public/
```

> 注意：主题通过 git submodule 引入，克隆仓库时请使用 `git clone --recurse-submodules` 或执行 `git submodule update --init --recursive`。

## 更新新闻动态（博客）

新闻动态就是博客功能，入口 `/blog/`。更新一篇新文章只需两步（无需本地环境）：

1. 打开仓库 `content/zh/blog/` 目录 → 参考 **`templates/blog-post-template.md`** 模板（或直接复制它改名）
2. 按模板填写标题/时间/分类/正文 → 点击 **Commit changes** 提交

约 1-2 分钟后网站自动更新。要点：

- 文件名随意（建议英文/拼音）；`title`、`date` 必填，其余可省略
- 配图：先上传图片到 `static/img/`（如 `static/img/blog/`），正文里用 `/img/blog/xxx.jpg` 引用
- 分类、标签可在侧栏看到，可自由新增
- 英文文章放在 `content/en/blog/`，格式相同
- 想先写不发布？把 `draft = true` 加进 front matter 即可

## 新增产品

产品中心是独立栏目（入口 `/products/`），每个产品一个页面，产品中心页自动卡片式列出。新增一个产品只需三步（无需本地环境）：

1. 打开仓库 **`templates/product-template.md`**，复制其中"中文产品"模板内容
2. 新建文件 `content/zh/products/产品英文短名/index.md`（目录名就是网址，如 `content/zh/products/agv-robot/index.md` → `/products/agv-robot/`），粘贴模板并修改标题/简介/正文
3. 点击 **Commit changes** 提交

约 1-2 分钟后自动上线。要点：

- `weight` 决定排序（数字越小越靠前：10、20、30 …）
- 产品主图：图片上传到 `static/img/products/` 后，把 `banner` 填为路径（如 `/img/products/agv-robot.jpg`）；不填则自动使用默认机器人封面图
- 正文可自由使用 Markdown：特性列表、技术参数表格、应用场景等
- 英文产品：同样步骤放到 `content/en/products/`（目录名与中文一致），内容翻译成英文
- 模板文件在仓库根 `templates/` 目录，不会被打包到网站

## 发布

推送 `main` 分支即触发 GitHub Actions 自动构建并部署到 `https://jiqiren.gs.cn`，无需手动操作。

## 待补充内容（占位待替换）

- [ ] 公司介绍、发展历程、资质荣誉（`content/zh/about.md`）
- [ ] 产品参数与案例（`content/zh/products/`、`data/`）
- [ ] 联系方式：电话、邮箱、地址（`hugo.toml` 与 `content/zh/contact.md`）
- [ ] Logo 与品牌图片（`static/img/logo.png` 等）
- [ ] 新闻文章（`content/zh/blog/`）
- [ ] 联系表单（可选）：注册 [Formspree](https://formspree.io) 后在 `hugo.toml` 填入 `formspree_action`
