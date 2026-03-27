# Short Reads Metagenomics Kraken2 Pipeline

基于 Snakemake 的二代测序（NGS）宏基因组 short reads 分析流程，主要步骤包括质控（fastp）、去宿主（bowtie2）、物种分类注释（Kraken2 + Bracken）。

## 作者信息

- **作者：** Yin Huamin
- **日期：** 2026.03.27
- **邮箱：** yinhm17@126.com

## 流程概览

```
Raw Reads (.fq.gz)
    │
    ▼
  fastp（质控 + 去接头）
    │
    ▼
  MultiQC（质控报告汇总）
    │
    ▼
  Bowtie2（去宿主序列）
    │
    ▼
  Kraken2（物种分类）
    │
    ▼
  Bracken（物种丰度估计）
    │
    ▼
  kreport2mpa + combine_mpa（结果汇总）
```

## 使用步骤

### 1. 创建并激活环境

使用 conda：

```bash
conda env create -f environment.yaml
conda activate kraken2_workflow
```

或者使用 micromamba：

```bash
micromamba create -f environment.yaml
micromamba activate kraken2_workflow
```

### 2. 修改 config.yaml 中的路径

根据你的实际数据和数据库路径，修改 `config.yaml` 中的以下字段：

```yaml
# 你的样本文件目录（paired-end reads 命名格式：{sample}_1.fq.gz, {sample}_2.fq.gz）
raw_dir: "01.rawdata"

# Bowtie2 宿主基因组索引路径
host_index: "/path/to/your/host_bowtie2_index"

# Kraken2 数据库路径
kraken2_db: "/path/to/your/kraken2_database"
```

### 3. 运行流程

```bash
snakemake --snakefile kraken2_snakemake.py --cores 4
```

运行前可以使用 dry-run 模式预览将要执行的任务：

```bash
snakemake --snakefile kraken2_snakemake.py --cores 4 -n
```

## 输入文件格式

样本文件需放置在 `raw_dir` 指定的目录下，命名格式为：

```
{sample}_1.fq.gz
{sample}_2.fq.gz
```

例如：

```
01.rawdata/
├── WT-C-12_1.fq.gz
├── WT-C-12_2.fq.gz
├── WT-C-13_1.fq.gz
└── WT-C-13_2.fq.gz
```

## 输出目录结构

```
02.cleandata/          # fastp 质控结果
├── {sample}.trimmed_1.fq.gz
├── {sample}.trimmed_2.fq.gz
├── {sample}.html      # fastp 单样本报告
├── {sample}.json
└── fastp_multiqc_report.html  # MultiQC 汇总报告

03.rm_host/            # 去宿主后的 reads
├── {sample}.rmhost.1.fastq
└── {sample}.rmhost.2.fastq

04.kraken2/            # Kraken2 + Bracken 分类结果
├── {sample}.kraken2          # Kraken2 原始输出
├── {sample}.k2report         # Kraken2 报告
├── {sample}.bracken          # Bracken 丰度估计
├── {sample}.breport          # Bracken 报告
├── {sample}.bracken.taxoname # MPA 格式结果
└── all_sample_merge.txt      # 所有样本合并结果
```

