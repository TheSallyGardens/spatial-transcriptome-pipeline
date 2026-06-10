# report - 生成 HTML 分析报告
rule generate_report:
    output:
        "results/reports/analysis_report.html"
    log:
        "logs/report/generate.log"
    run:
        from pathlib import Path
        Path(output[0]).parent.mkdir(parents=True, exist_ok=True)
        html = """<!doctype html>
<html><head><meta charset="utf-8"><title>分析报告</title></head>
<body><h1>空间转录组分析报告</h1>
<p>由 spstpipe 生成。</p></body></html>
"""
        Path(output[0]).write_text(html, encoding="utf-8")