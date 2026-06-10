configfile: "config/config.yaml"
configfile: "config/samples.yaml"

include: "workflow/rules/preprocessing.smk"
include: "workflow/rules/basic_analysis.smk"
include: "workflow/rules/visualization.smk"
include: "workflow/rules/report.smk"

for plugin in config.get("plugins", []):
    if plugin.get("enabled", False):
        include: f"workflow/rules/{plugin['name']}.smk"


rule all:
    input:
        "results/reports/analysis_report.html"
