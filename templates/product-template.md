# 产品页模板 — 新增产品时复制本文件使用

## 使用方法（中文产品）

1. 复制本文件到：`content/zh/products/你的产品英文短名/index.md`
   （目录名 = 产品页网址，例如 `content/zh/products/agv-robot/index.md` → 网址 `/products/agv-robot/`）
2. 修改下面的标题、简介、正文
3. （可选）放一张产品主图到 `static/img/products/` 目录，并把 `banner` 填为图片路径；
   不填 banner 时自动使用默认机器人封面图
4. 英文版：复制到 `content/en/products/同一英文短名/index.md`，内容翻译成英文
5. 提交推送，等待 1-2 分钟自动部署上线

排序：`weight` 数字越小越靠前（10、20、30 …）。

```markdown
+++
title = "产品名称"
description = "产品一句话简介（列表页和搜索引擎显示）"
keywords = ["关键词1", "关键词2"]
weight = 40
# 产品主图：图片放到 static/img/products/ 后填路径，例如 "/img/products/agv-robot.jpg"；
# 留空则显示默认机器人封面图
banner = ""
+++

# 产品名称

产品简介：一句话说清这是什么、解决什么问题。

## 产品特性

- 特性一
- 特性二
- 特性三

## 技术参数

| 参数 | 数值 |
|------|------|
| 型号 |  |
| 负载 |  |
| 精度 |  |

## 应用场景

- 场景一
- 场景二

如需了解更多，欢迎[联系我们](/contact/)。
```

## 英文产品（content/en/products/同一英文短名/index.md）

```markdown
+++
title = "Product Name"
description = "One-line product intro (shown in list page and search engines)"
keywords = ["keyword1", "keyword2"]
weight = 40
# banner: put the image in static/img/products/ and set the path, e.g. "/img/products/agv-robot.jpg";
# leave empty to use the default robot cover
banner = ""
+++

# Product Name

One-line intro: what it is and what problem it solves.

## Key Features

- Feature 1
- Feature 2
- Feature 3

## Specifications

| Parameter | Value |
|-----------|-------|
| Model     |  |
| Payload   |  |
| Accuracy  |  |

## Applications

- Application 1
- Application 2

For more information, please [contact us](/en/contact/).
```
