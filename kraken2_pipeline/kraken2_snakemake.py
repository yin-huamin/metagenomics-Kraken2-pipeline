import os
from glob import glob

configfile: "config.yaml"

RAW_DIR = config["raw_dir"]
FASTP_DIR = config["fastp_dir"]
RMHOST_DIR = config["rmhost_dir"]
KRAKEN_DIR = config["kraken_dir"]

samples = sorted(glob_wildcards(os.path.join(RAW_DIR, "{sample}_1.fq.gz")).sample)

rule all:
    input:
        expand(os.path.join(FASTP_DIR, "{sample}.trimmed_1.fq.gz"), sample=samples),
        expand(os.path.join(FASTP_DIR, "{sample}.trimmed_2.fq.gz"), sample=samples),
        os.path.join(FASTP_DIR, "fastp_multiqc_report.html"),

        expand(os.path.join(RMHOST_DIR, "{sample}.rmhost.1.fastq"), sample=samples),
        expand(os.path.join(RMHOST_DIR, "{sample}.rmhost.2.fastq"), sample=samples),

        expand(os.path.join(KRAKEN_DIR, "{sample}.kraken2"), sample=samples),
        expand(os.path.join(KRAKEN_DIR, "{sample}.k2report"), sample=samples),
        expand(os.path.join(KRAKEN_DIR, "{sample}.bracken"), sample=samples),
        expand(os.path.join(KRAKEN_DIR, "{sample}.breport"), sample=samples),
        expand(os.path.join(KRAKEN_DIR, "{sample}.bracken.taxoname"), sample=samples),

        os.path.join(KRAKEN_DIR, "all_sample_merge.txt"),

rule fastp:
    input:
        r1=os.path.join(RAW_DIR, "{sample}_1.fq.gz"),
        r2=os.path.join(RAW_DIR, "{sample}_2.fq.gz")
    output:
        r1=os.path.join(FASTP_DIR, "{sample}.trimmed_1.fq.gz"),
        r2=os.path.join(FASTP_DIR, "{sample}.trimmed_2.fq.gz"),
        html=os.path.join(FASTP_DIR, "{sample}.html"),
        json=os.path.join(FASTP_DIR, "{sample}.json")
    threads: config["threads"]["fastp"]
    params:
        env=config["envs"]["kraken2"]
    log:
        os.path.join(FASTP_DIR, "logs", "{sample}.fastp.log")
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH"
        mkdir -p {FASTP_DIR} {FASTP_DIR}/logs
        fastp \
          -i {input.r1} \
          -I {input.r2} \
          -o {output.r1} \
          -O {output.r2} \
          -h {output.html} \
          -j {output.json} \
          --trim_poly_g \
          -q 20 \
          -w {threads} \
          > {log} 2>&1
        """

rule multiqc_fastp:
    input:
        expand(os.path.join(FASTP_DIR, "{sample}.json"), sample=samples),
        expand(os.path.join(FASTP_DIR, "{sample}.html"), sample=samples)
    output:
        os.path.join(FASTP_DIR, "fastp_multiqc_report.html")
    params:
        env=config["envs"]["kraken2"]
    log:
        os.path.join(FASTP_DIR, "logs", "multiqc.log")
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH" && \
        mkdir -p {FASTP_DIR}/logs && \
        multiqc {FASTP_DIR} -n fastp_multiqc_report.html -o {FASTP_DIR} > {log} 2>&1
        """

rule remove_host:
    input:
        r1=os.path.join(FASTP_DIR, "{sample}.trimmed_1.fq.gz"),
        r2=os.path.join(FASTP_DIR, "{sample}.trimmed_2.fq.gz")
    output:
        r1=os.path.join(RMHOST_DIR, "{sample}.rmhost.1.fastq"),
        r2=os.path.join(RMHOST_DIR, "{sample}.rmhost.2.fastq"),
        log=os.path.join(RMHOST_DIR, "{sample}_bowtie2.log")
    threads: config["threads"]["bowtie2"]
    params:
        index=config["host_index"],
        prefix=os.path.join(RMHOST_DIR, "{sample}.rmhost.fastq"),
        env=config["envs"]["kraken2"]
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH" && \
        mkdir -p {RMHOST_DIR} && \
        bowtie2 \
          -p {threads} \
          -x {params.index} \
          -1 {input.r1} \
          -2 {input.r2} \
          --un-conc {params.prefix} \
          -S /dev/null \
          2> {output.log}
        """

rule kraken2:
    input:
        r1=os.path.join(RMHOST_DIR, "{sample}.rmhost.1.fastq"),
        r2=os.path.join(RMHOST_DIR, "{sample}.rmhost.2.fastq")
    output:
        out=os.path.join(KRAKEN_DIR, "{sample}.kraken2"),
        report=os.path.join(KRAKEN_DIR, "{sample}.k2report")
    threads: config["threads"]["kraken2"]
    params:
        db=config["kraken2_db"],
        env=config["envs"]["kraken2"]
    log:
        os.path.join(KRAKEN_DIR, "logs", "{sample}.kraken2.log")
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH" && \
        mkdir -p {KRAKEN_DIR} {KRAKEN_DIR}/logs && \
        kraken2 \
          --threads {threads} \
          --db {params.db} \
          --report {output.report} \
          --paired {input.r1} {input.r2} \
          > {output.out} 2> {log}
        """

rule bracken:
    input:
        report=os.path.join(KRAKEN_DIR, "{sample}.k2report")
    output:
        bracken=os.path.join(KRAKEN_DIR, "{sample}.bracken"),
        breport=os.path.join(KRAKEN_DIR, "{sample}.breport")
    params:
        db=config["kraken2_db"],
        threshold=config["bracken_threshold"],
        env=config["envs"]["kraken2"]
    log:
        os.path.join(KRAKEN_DIR, "logs", "{sample}.bracken.log")
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH" && \
        bracken \
          -d {params.db} \
          -i {input.report} \
          -o {output.bracken} \
          -w {output.breport} \
          -t {params.threshold} \
          > {log} 2>&1
        """

rule breport_to_mpa:
    input:
        os.path.join(KRAKEN_DIR, "{sample}.breport")
    output:
        os.path.join(KRAKEN_DIR, "{sample}.bracken.taxoname")
    params:
        env=config["envs"]["kraken2"]
    log:
        os.path.join(KRAKEN_DIR, "logs", "{sample}.kreport2mpa.log")
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH" && \
        kreport2mpa.py \
          -r {input} \
          -o {output} \
          > {log} 2>&1
        """

rule combine_mpa:
    input:
        expand(os.path.join(KRAKEN_DIR, "{sample}.bracken.taxoname"), sample=samples)
    output:
        os.path.join(KRAKEN_DIR, "all_sample_merge.txt")
    params:
        indir=KRAKEN_DIR,
        env=config["envs"]["kraken2"]
    log:
        os.path.join(KRAKEN_DIR, "logs", "combine_mpa.log")
    shell:
        r"""
        export PATH="{params.env}/bin:$PATH" && \
        cd {params.indir} && \
        combine_mpa.py -i *.bracken.taxoname -o all_sample_merge.txt \
        > logs/combine_mpa.log 2>&1
        """