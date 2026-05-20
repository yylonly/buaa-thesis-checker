#!/usr/bin/env python3
"""
HTML模板填充器 - 使用预定义的HTML模板生成论文审核报告

使用方法:
    python3 template_filler.py --llm-data '<json>' --output <output_dir>
    python3 template_filler.py --llm-data '<json>' --template <template_path> --output <output_dir>

模板变量说明:
    {{PAPER_TITLE}}          - 论文标题
    {{AUDIT_DATE}}            - 审核日期
    {{TRACE_STATUS}}          - 追溯关系状态
    {{TRACE_DETAIL}}          - 追溯关系详情
    {{PROBLEMS_TABLE_ROWS}}   - 问题分析表格行
    {{INNOVATIONS_TABLE_ROWS}} - 创新点表格行
    {{RQ_TABLE_ROWS}}         - 研究问题表格行
    {{DATASETS_TABLE_ROWS}}   - 数据集表格行
    {{METRICS_TABLE_ROWS}}    - 评价指标表格行
    {{KEY_FINDINGS_LIST}}     - 关键发现列表
    {{LIMITATIONS_LIST}}      - 局限性列表
    {{CONTRIBUTIONS_TABLE_ROWS}} - 贡献点表格行
    {{METHOD_VS_BASELINE_CARDS}} - 方法对比卡片
    {{BASELINES_TABLE_ROWS}}  - Baseline表格行
    {{EXPERIMENTS_TABLE_ROWS}} - 实验表格行
    {{INCREMENTAL_TABLE_ROWS}} - 增量改进表格行
    {{SCORES_GRID}}           - 评分网格
    {{CONSTRAINT_CHECK_ROWS}} - 约束检查行
    {{FINAL_CONTRIBUTIONS_ROWS}} - 最终贡献行
    {{STRENGTHS_LIST}}        - 优点列表
    {{WEAKNESSES_LIST}}        - 不足列表
"""

import os
import sys
import json
import argparse
from datetime import datetime


# 默认模板路径
DEFAULT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'references',
    'paper_audit_template.html'
)


def load_template(template_path: str) -> str:
    """加载HTML模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def build_problems_table_rows(problems: list) -> str:
    """构建问题分析表格行"""
    if not problems:
        return '      <tr><td colspan="5">暂无问题分析数据</td></tr>\n'

    rows = ""
    for p in problems:
        problem_id = p.get('问题编号', '')
        problem_desc = p.get('问题描述', '')
        existing_perf = p.get('现有方法表现', '')
        root_cause = p.get('问题根源', '')
        linked = p.get('对应创新点', [])
        linked_str = ', '.join(linked) if linked else '未对应'
        rows += f"""      <tr>
        <td class='problem-id'>{problem_id}</td>
        <td>{problem_desc}</td>
        <td>{existing_perf}</td>
        <td>{root_cause}</td>
        <td class='linked'>{linked_str}</td>
      </tr>\n"""
    return rows


def build_innovations_table_rows(innovations: list) -> str:
    """构建创新点表格行"""
    if not innovations:
        return '      <tr><td colspan="7">暂无创新点数据</td></tr>\n'

    rows = ""
    for m in innovations:
        innovation_id = m.get('创新编号', m.get('innovation_id', ''))
        innovation = m.get('创新点', m.get('innovation', ''))
        section = m.get('section', '')
        details = m.get('details', '')
        innovation_type = m.get('创新类型', '待确认')
        linked = m.get('解决的问题', [])
        linked_str = ', '.join(linked) if linked else '未对应'
        status = m.get('status', '✅')
        status_class = 'pass' if '✅' in status else ('fail' if '❌' in status else 'warning')
        rows += f"""      <tr>
        <td class='innovation-id'>{innovation_id}</td>
        <td>{innovation}</td>
        <td>{section}</td>
        <td>{details}</td>
        <td>{innovation_type}</td>
        <td class='linked'>→ {linked_str}</td>
        <td class='{status_class}'>{status}</td>
      </tr>\n"""
    return rows


def build_rq_table_rows(rqs: list) -> str:
    """构建研究问题表格行"""
    if not rqs:
        return '      <tr><td colspan="3">暂无研究问题数据</td></tr>\n'

    rows = ""
    for rq in rqs:
        rq_id = rq.get('rq_id', '')
        rq_desc = rq.get('rq描述', '')
        linked = rq.get('对应的创新点', [])
        linked_str = ', '.join(linked) if linked else '未对应'
        rows += f"      <tr><td>{rq_id}</td><td>{rq_desc}</td><td>{linked_str}</td></tr>\n"
    return rows


def build_datasets_table_rows(datasets: list) -> str:
    """构建数据集表格行"""
    if not datasets:
        return '      <tr><td colspan="3">暂无数据集数据</td></tr>\n'

    rows = ""
    for ds in datasets:
        if isinstance(ds, dict):
            rows += f"      <tr><td>{ds.get('dataset_name', '')}</td><td>{ds.get('size', '')}</td><td>{ds.get('description', '')}</td></tr>\n"
        else:
            rows += f"      <tr><td>{ds}</td><td></td><td></td></tr>\n"
    return rows


def build_metrics_table_rows(metrics: list) -> str:
    """构建评价指标表格行"""
    if not metrics:
        return '      <tr><td colspan="3">暂无指标数据</td></tr>\n'

    rows = ""
    for mt in metrics:
        if isinstance(mt, dict):
            higher = '↑' if mt.get('higher_better', True) else '↓'
            rows += f"      <tr><td>{mt.get('metric_name', '')}</td><td>{mt.get('definition', '')}</td><td>{higher}</td></tr>\n"
        else:
            rows += f"      <tr><td>{mt}</td><td></td><td></td></tr>\n"
    return rows


def build_key_findings_list(findings: list) -> str:
    """构建关键发现列表"""
    if not findings:
        return '      <li>暂无关键发现数据</li>\n'
    return ''.join([f"      <li>{f}</li>\n" for f in findings])


def build_limitations_list(limitations: list) -> str:
    """构建局限性列表"""
    if not limitations:
        return '      <li>暂无局限性数据</li>\n'

    rows = ""
    for lim in limitations:
        lim_text = lim.get('limitation', lim) if isinstance(lim, dict) else lim
        acknowledged = '✅' if (isinstance(lim, dict) and lim.get('acknowledged_by_paper', False)) else ''
        rows += f"      <li>{lim_text} {acknowledged}</li>\n"
    return rows


def build_contributions_table_rows(contributions: list) -> str:
    """构建贡献点表格行"""
    if not contributions:
        return '      <tr><td colspan="3">暂无数据</td></tr>\n'

    rows = ""
    for c in contributions:
        point = c.get('point', '')
        method = c.get('method', '')
        evaluation = c.get('evaluation', '')
        eval_class = 'pass' if '✅' in evaluation else ('fail' if '❌' in evaluation else 'warning')
        rows += f"      <tr><td>{point}</td><td>{method}</td><td class='{eval_class}'>{evaluation}</td></tr>\n"
    return rows


def build_method_vs_baseline_cards(comparisons: list) -> str:
    """构建方法对比卡片"""
    if not comparisons:
        return '    <p class="none">暂无详细对比数据</p>'

    cards = ""
    for item in comparisons:
        method_name = item.get('method_name', '未命名方法')
        baseline = item.get('baseline', 'Baseline')
        improvements = item.get('improvements', [])
        metrics = item.get('metrics', [])

        improvements_li = ''.join([f"          <li>{imp}</li>\n" for imp in improvements]) if improvements else "          <li class='none'>未提供</li>\n"

        # 处理metrics
        if metrics:
            if isinstance(metrics[0], dict):
                metrics_li = ''.join([f"          <li>{m.get('metric', '')}: {m.get('baseline_value', '')} → {m.get('proposed_value', '')} ({m.get('improvement', '')})</li>\n" for m in metrics])
            else:
                metrics_li = ''.join([f"          <li>{m}</li>\n" for m in metrics])
        else:
            metrics_li = "          <li class='none'>未提供</li>\n"

        cards += f"""
        <div class="comparison-card">
          <h4>{method_name} vs {baseline}</h4>
          <table class='inner-table'>
            <tr><th>对比维度</th><th>内容</th></tr>
            <tr><td class='label'>具体改进</td><td><ul>{improvements_li}</ul></td></tr>
            <tr><td class='label'>性能指标</td><td><ul>{metrics_li}</ul></td></tr>
          </table>
        </div>
"""
    return cards


def build_baselines_table_rows(baselines: list) -> str:
    """构建Baseline表格行"""
    if not baselines:
        return '      <tr><td colspan="3">暂无数据</td></tr>\n'

    rows = ""
    for b in baselines:
        name = b.get('name', '')
        description = b.get('description', '')
        section = b.get('section', '')
        rows += f"      <tr><td>{name}</td><td>{description}</td><td>{section}</td></tr>\n"
    return rows


def build_experiments_table_rows(experiments: list) -> str:
    """构建实验表格行"""
    if not experiments:
        return '      <tr><td colspan="3">暂无数据</td></tr>\n'

    rows = ""
    for e in experiments:
        exp_type = e.get('type', '')
        section = e.get('section', '')
        description = e.get('description', '')
        rows += f"      <tr><td>{exp_type}</td><td>{section}</td><td>{description}</td></tr>\n"
    return rows


def build_incremental_table_rows(incremental: list) -> str:
    """构建增量改进表格行"""
    if not incremental:
        return '      <tr><td colspan="2">暂无数据</td></tr>\n'

    rows = ""
    for i in incremental:
        contribution = i.get('contribution', '')
        assessment = i.get('assessment', '')
        assess_class = 'pass' if '原创' in assessment or 'novel' in assessment.lower() else ('warning' if '增量' in assessment else '')
        rows += f"      <tr><td>{contribution}</td><td class='{assess_class}'>{assessment}</td></tr>\n"
    return rows


def build_scores_grid(scores: list) -> str:
    """构建评分网格"""
    if not scores:
        return '      <div class="score-item"><span>暂无评分数据</span></div>'

    grid = ""
    for s in scores:
        dimension = s.get('dimension', '')
        result = s.get('result', '')
        if '✅' in result:
            status_class = 'pass'
        elif '❌' in result:
            status_class = 'fail'
        else:
            status_class = 'warning'
        grid += f"""      <div class="score-item {status_class}">
        <span class="dimension">{dimension}</span>
        <span class="result {status_class}">{result}</span>
      </div>
"""
    return grid


def build_constraint_check_rows(constraint_check: dict) -> str:
    """构建约束检查行"""
    if not constraint_check:
        return '      <tr><td colspan="3">暂无约束检查数据</td></tr>\n'

    rows = ""
    for category, data in constraint_check.items():
        count = data.get('count', 0)
        exceeds = data.get('exceeds', False)
        status_icon = '❌' if exceeds else '✅'
        status_text = '超过限制' if exceeds else '符合要求'
        rows += f"      <tr class='{'fail' if exceeds else 'pass'}'><td>{category}</td><td>{count}个</td><td>{status_icon} {status_text}</td></tr>\n"
    return rows


def build_final_contributions_rows(final_contributions: dict) -> str:
    """构建最终贡献行"""
    if not final_contributions:
        return '      <tr><td colspan="2">暂无最终贡献数据</td></tr>\n'

    rows = ""
    for category, items in final_contributions.items():
        if isinstance(items, list):
            items_str = '<br>'.join([f"• {item}" if isinstance(item, str) else f"• {item.get('描述', item)}" for item in items])
        else:
            items_str = str(items)
        rows += f"      <tr><td><strong>{category}</strong></td><td>{items_str}</td></tr>\n"
    return rows


def build_strengths_list(strengths: list) -> str:
    """构建优点列表"""
    if not strengths:
        return '      <li>暂无明确优点</li>\n'
    return ''.join([f"      <li>{s}</li>\n" for s in strengths])


def build_weaknesses_list(weaknesses: list) -> str:
    """构建不足列表"""
    if not weaknesses:
        return '      <li>暂无明显不足</li>\n'
    return ''.join([f"      <li>{w}</li>\n" for w in weaknesses])


def fill_template(template: str, audit_data: dict, timestamp: str) -> str:
    """使用审核数据填充模板"""

    # 基本信息
    paper_title = audit_data.get('paper_title', '论文内容审核报告')
    basic_info = audit_data.get('basic_info', {})
    audit_date = basic_info.get('审核时间', timestamp)

    # 追溯关系
    summary = audit_data.get('summary', {})
    trace_check = summary.get('traceability_check', {})
    trace_ok = trace_check.get('problems_with_solutions', False) and trace_check.get('solutions_with_evaluation', False)
    trace_status = '✅ 追溯关系完整' if trace_ok else '⚠️ 追溯关系需完善'
    trace_detail = f"问题→创新: {'✅' if trace_check.get('problems_with_solutions', False) else '❌'} | 创新→评估: {'✅' if trace_check.get('solutions_with_evaluation', False) else '❌'} | 评估→问题: {'✅' if trace_check.get('evaluation_traces_to_problems', False) else '❌'}"

    # 替换模板变量
    replacements = {
        '{{PAPER_TITLE}}': paper_title,
        '{{AUDIT_DATE}}': audit_date,
        '{{TRACE_STATUS}}': trace_status,
        '{{TRACE_DETAIL}}': trace_detail,
        '{{PROBLEMS_TABLE_ROWS}}': build_problems_table_rows(audit_data.get('一_主要问题分析', [])),
        '{{INNOVATIONS_TABLE_ROWS}}': build_innovations_table_rows(audit_data.get('二_方法创新性', audit_data.get('method_innovations', []))),
        '{{RQ_TABLE_ROWS}}': build_rq_table_rows(audit_data.get('三_评估验证', {}).get('research_questions', [])),
        '{{DATASETS_TABLE_ROWS}}': build_datasets_table_rows(audit_data.get('三_评估验证', {}).get('datasets', [])),
        '{{METRICS_TABLE_ROWS}}': build_metrics_table_rows(audit_data.get('三_评估验证', {}).get('metrics', [])),
        '{{KEY_FINDINGS_LIST}}': build_key_findings_list(audit_data.get('三_评估验证', {}).get('results', {}).get('关键发现', [])),
        '{{LIMITATIONS_LIST}}': build_limitations_list(audit_data.get('三_评估验证', {}).get('limitations', [])),
        '{{CONTRIBUTIONS_TABLE_ROWS}}': build_contributions_table_rows(audit_data.get('contributions', [])),
        '{{METHOD_VS_BASELINE_CARDS}}': build_method_vs_baseline_cards(audit_data.get('method_vs_baseline', [])),
        '{{BASELINES_TABLE_ROWS}}': build_baselines_table_rows(audit_data.get('baselines', [])),
        '{{EXPERIMENTS_TABLE_ROWS}}': build_experiments_table_rows(audit_data.get('experiments', [])),
        '{{INCREMENTAL_TABLE_ROWS}}': build_incremental_table_rows(audit_data.get('incremental_improvements', [])),
        '{{SCORES_GRID}}': build_scores_grid(audit_data.get('overall_scores', [])),
        '{{CONSTRAINT_CHECK_ROWS}}': build_constraint_check_rows(audit_data.get('constraint_check', {})),
        '{{FINAL_CONTRIBUTIONS_ROWS}}': build_final_contributions_rows(audit_data.get('final_contributions', {})),
        '{{STRENGTHS_LIST}}': build_strengths_list(summary.get('strengths', [])),
        '{{WEAKNESSES_LIST}}': build_weaknesses_list(summary.get('weaknesses', [])),
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def generate_report_from_template(
    llm_data: dict,
    template_path: str = None,
    output_dir: str = "."
) -> str:
    """使用模板生成HTML报告"""

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 加载模板
    if template_path is None:
        template_path = DEFAULT_TEMPLATE_PATH

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    template = load_template(template_path)

    # 填充模板
    html_content = fill_template(template, llm_data, date_str)

    # 保存报告
    output_path = os.path.join(output_dir, f"paper_audit_report_{timestamp}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


def main():
    parser = argparse.ArgumentParser(description='使用HTML模板生成论文审核报告')
    parser.add_argument('--llm-data', '-d', required=True, help='LLM分析结果的JSON数据')
    parser.add_argument('--template', '-t', default=None, help='HTML模板路径（可选）')
    parser.add_argument('--output', '-o', default='.', help='输出目录（可选）')

    args = parser.parse_args()

    # 解析JSON数据
    try:
        llm_data = json.loads(args.llm_data)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败: {e}")
        sys.exit(1)

    # 生成报告
    try:
        output_path = generate_report_from_template(
            llm_data=llm_data,
            template_path=args.template,
            output_dir=args.output
        )
        print(f"✅ HTML报告已保存: {output_path}")
    except Exception as e:
        print(f"错误: 生成报告失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
