# workflow/scripts/report.py
import scanpy as sc
from pathlib import Path
from datetime import datetime

def generate_html_report(samples_info, output_file):
    """生成HTML分析报告"""

    # 获取当前时间
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spatial Transcriptomics Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
        }}
        .sample-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .sample-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #eee;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}
        .sample-title {{
            font-size: 1.5em;
            color: #333;
            margin: 0;
        }}
        .platform-badge {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .figure-section {{
            margin-top: 20px;
        }}
        .figure-section h3 {{
            color: #333;
            margin-bottom: 15px;
        }}
        .figure-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        .figure-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 10px;
        }}
        .figure-card img {{
            width: 100%;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Spatial Transcriptomics Analysis Report</h1>
        <p>Generated on: {report_date}</p>
    </div>
"""

    for sample in samples_info:
        html_content += f"""
    <div class="sample-card">
        <div class="sample-header">
            <h2 class="sample-title">{sample['id']}</h2>
            <span class="platform-badge">{sample['platform']}</span>
        </div>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{sample['n_cells']:,}</div>
                <div class="stat-label">Cells/Spots</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{sample['n_genes']:,}</div>
                <div class="stat-label">Genes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{sample.get('n_clusters', 'N/A')}</div>
                <div class="stat-label">Clusters</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{sample.get('n_cell_types', 'N/A')}</div>
                <div class="stat-label">Cell Types</div>
            </div>
        </div>
"""

        if sample.get('figures'):
            html_content += '        <div class="figure-section">\n'
            html_content += '            <h3>Visualizations</h3>\n'
            html_content += '            <div class="figure-grid">\n'
            for fig in sample['figures']:
                html_content += f"""
                <div class="figure-card">
                    <img src="{fig['path']}" alt="{fig['title']}">
                </div>
"""
            html_content += '            </div>\n'
            html_content += '        </div>\n'

        html_content += '    </div>\n'

    html_content += f"""
    <div class="footer">
        <p>Spatial Transcriptome Pipeline v1.0 | Powered by Scanpy & Squidpy</p>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

# Snakemake script接口
if __name__ == "__snakemake__":
    output_file = snakemake.output[0]

    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    sample_ids = [s["id"] for s in config["samples"]]

    samples_info = []
    for sample_id in sample_ids:
        adata_path = f"results/{sample_id}/data/annotated_adata.h5ad"
        if Path(adata_path).exists():
            adata = sc.read_h5ad(adata_path)
            n_cells = adata.n_obs
            n_genes = adata.n_vars
            n_clusters = len(adata.obs.get('louvain', []).unique()) if 'louvain' in adata.obs else 'N/A'

            # 尝试获取细胞类型数量
            n_cell_types = 'N/A'
            if 'cell_type' in adata.obs:
                n_cell_types = len(adata.obs['cell_type'].unique())
            elif 'celltype' in adata.obs:
                n_cell_types = len(adata.obs['celltype'].unique())

            platform = adata.uns.get("platform", "unknown")

            # 收集可视化文件
            figures = []
            viz_dir = Path(f"results/{sample_id}/visualization")
            if viz_dir.exists():
                for img_file in viz_dir.glob("*.png"):
                    figures.append({
                        "title": img_file.stem,
                        "path": str(img_file.relative_to(Path(output_file).parent))
                    })

            samples_info.append({
                "id": sample_id,
                "platform": platform,
                "n_cells": n_cells,
                "n_genes": n_genes,
                "n_clusters": n_clusters,
                "n_cell_types": n_cell_types,
                "figures": figures
            })
        else:
            samples_info.append({
                "id": sample_id,
                "platform": "N/A",
                "n_cells": 0,
                "n_genes": 0,
                "n_clusters": "N/A",
                "n_cell_types": "N/A",
                "figures": []
            })

    generate_html_report(samples_info, output_file)