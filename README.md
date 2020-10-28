# Ancy 小鹤双拼双形 （安系小鹤） Rime 配置方案

## 方案介绍

小鹤双拼双形方案扩展。

主要修改包括：

- 单字输入的智能化：辅助码（形码）变为可选，可以自行选择是否加入辅助码，也可通过辅助码进行选词（词频可以记录）。
- 词组输入的智能化：词组中任意字都可通过加入辅助码（形码）作为辅助信息帮助得到更好的结果，也可以不加入。输入时未采用原小鹤双拼双形的首字母组合的方式，而是采用直接输入双拼。例如输入：小鹤双拼，原方式的输入为：xhup （声母组合），现在的方式输入为：xnheulpb ，同时可以在任意位置插入辅助码，例如可以输入为 xnhedulpb （鹤字加入形码）
- 自定义词：加入了自定义的词组（通过使用搜狗的细胞词库）。目前随机加入了一些词库。如果有特定细胞词库的需求，可以提 issue 。（也可以利用 [`src/ancyflypy.ipynb`](src/ancyflypy.ipynb) 自行构造）

## 使用方法

下载 "ancy_flypy_extend.dict.yaml" 和 "ancy_flypy_extend.schema.yaml" ，然后拷至 rime 配置目录，linux 下 fcitx 为 "~/.config/fcitx/rime/" 

接下来找到 rime 配置文件目录下的 "default.custom.yaml" ，在其中的 schema 部分添加 "ancy_flypy_extend" schema ，最后重启使用。

东风破：`bash rime-install Escapingbug/ancyflypy`

## Future Work

- 加入快速导入搜狗输入法细胞词库功能