# StockDemo K线开发 - 2026-01-31

## 任务
为星环科技（688011）绘制 K 线，支持每日分时图分割显示。

## 思考过程
1. 按模板创建项目结构（README, requirements.txt, docs/, scripts/, data/）
2. 遇到依赖安装问题（Python 虚拟环境、版本兼容）
3. 处理 akshare 返回的中文列名映射
4. 解决 mplfinance 的 mav=None 参数问题
5. 实现每日分割循环绘图功能

## 行动步骤
1. 创建 stockdemo 项目结构
2. 配置 requirements.txt（akshare, mplfinance, pandas, matplotlib）
3. 编写 main.py：
   - 命令行参数解析（argparse）
   - 数据获取（akshare.stock_zh_a_hist）
   - 数据处理（中英文列名映射）
   - K 线绘制（mplfinance）
   - 每日分割模式（循环遍历每一天）
4. 安装依赖（venv + pip）
5. 测试基本功能和每日分割功能

## 关键代码片段
```python
# 中英文列名映射
column_mapping = {
    '日期': 'Date', '开盘': 'Open', '收盘': 'Close',
    '最高': 'High', '最低': 'Low', '成交量': 'Volume'
}

# 动态构建绘图参数
plot_kwargs = {'type': 'candle', 'style': style, 'volume': True}
if mav:
    plot_kwargs['mav'] = mav
```

## 注意事项
- akshare 返回中文列名，需映射为英文
- mplfinance 的 mav 参数不能为 None，需条件传递
- Python 虚拟环境用 `python3 -m venv venv`
- 每日分割模式：遍历唯一日期，每天生成分割图片
