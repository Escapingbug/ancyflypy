# Ancy 小鹤双拼双形 （安系小鹤） Rime 配置方案

## 方案介绍

小鹤双拼双形方案扩展，单字直接沿用了原小鹤双拼双形方案，词组方面做了改动和扩展。

词组方面使用传统双拼打字，在末位可以添加词组末字的形码来降低重码率。

（原方案可以在任意位置添加形码，但是 Rime 此时占用内存极大，linux 下占用将近 1G 内存，而根据实际情况来看，末字添加形码已经基本不需要翻页，则可以接受）


## 方案优势

- 快速选词，且选词方案与自定义词语输入保持一致
- 词库添加，使用了 jieba 的常用词词库搜狗的计算机细胞词库，后续将进一步添加快速导入细胞词库方法，现有词语约 58 万，能够不错的覆盖日常使用

有了以上两点，本版本可以既可以做为原版的扩展（词库添加），也可以作为普通双拼的辅助

## 使用方法

下载 "ancy_flypy_extend.dict.yaml" 和 "ancy_flypy_extend.schema.yaml" ，然后拷至 rime 配置目录，linux 下 fcitx 为 "~/.config/fcitx/rime/" 

接下来找到 rime 配置文件目录下的 "default.custom.yaml" ，在其中的 schema 部分添加 "ancy_flypy_extend" schema ，最后重启使用。

东风破：`bash rime-install Escapingbug/ancyflypy`

## Future Work

- 重构源码，统一接口（cli 接口）
- 加入快速导入搜狗输入法细胞词库功能
- 自动安装
