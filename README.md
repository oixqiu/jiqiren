# jiqiren — 机器人企业官网

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
│   │   ├── products.md  # 产品中心
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

## 发布

推送 `main` 分支即触发 GitHub Actions 自动构建并部署到 `https://jiqiren.gs.cn`，无需手动操作。

## 待补充内容（占位待替换）

- [ ] 公司介绍、发展历程、资质荣誉（`content/zh/about.md`）
- [ ] 产品参数与案例（`content/zh/products.md`、`data/`）
- [ ] 联系方式：电话、邮箱、地址（`hugo.toml` 与 `content/zh/contact.md`）
- [ ] Logo 与品牌图片（`static/img/logo.png` 等）
- [ ] 新闻文章（`content/zh/blog/`）
- [ ] 联系表单（可选）：注册 [Formspree](https://formspree.io) 后在 `hugo.toml` 填入 `formspree_action`
