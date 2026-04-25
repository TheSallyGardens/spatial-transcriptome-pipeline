configfile: "config/config.yaml"
configfile: "config/samples.yaml"

# 加载所有插件规则
for plugin in config.get("plugins", []):
    if plugin.get("enabled", False):
        include: f"workflow/rules/{plugin['name']}.smk"

include: "workflow/rules/preprocessing.smk"
include: "workflow/rules/basic_analysis.smk"
include: "workflow/rules/visualization.smk"
include: "workflow/rules/report.smk"

rule all:
    input:
        "results/reports/analysis_report.html"
