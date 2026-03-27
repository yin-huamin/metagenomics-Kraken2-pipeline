# Metagenomics Pipeline

宏基因组测序分析流程整合

## 作者信息

- **作者：** Yin Huamin
- **日期：** 2026.03.27（持续更新中）
- **邮箱：** yinhm17@126.com

## Table of Contents

**Short Reads**

| Pipeline | 说明 |
|----------|------|
| kraken2_pipeline | Kraken2 + Bracken 物种分类注释 |
| HUMAnN4_pipeline | 功能通路分析 |
| MetaPhlAn4_pipeline | 物种组成分析 |
| assembly_pipeline | 宏基因组组装 |
| binning_pipeline | 基因组分箱 |

**Long Reads**

| Pipeline | 说明 |
|----------|------|
| HiFi-MAGs-pipeline | HiFi 长读长 MAGs 构建 |
| assembly_pipeline | 长读长宏基因组组装 |

## 使用步骤

### 1. 创建并激活环境

每个 pipeline 目录下提供了对应的 `environment.yaml`，选择 conda 或 micromamba 创建环境：

```bash
# conda
conda env create -f environment.yaml
conda activate <env_name>

# 或 micromamba
micromamba create -f environment.yaml
micromamba activate <env_name>
```

### 2. 修改配置文件

根据实际数据和数据库路径，修改对应 pipeline 目录下的 `config.yaml`。

### 3. 运行流程

```bash
snakemake --snakefile snakemake.py --cores 4
```

运行前可以使用 dry-run 模式预览将要执行的任务：

```bash
snakemake --snakefile snakemake.py --cores 4 -n
```

> `-c 4` / `--cores 4`：指定使用的 CPU 核心数，默认推荐 4，可根据服务器资源调整。

