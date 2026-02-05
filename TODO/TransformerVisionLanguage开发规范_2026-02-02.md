# Transformer Vision-Language 模型开发规范

**创建日期**: 2026-02-02
**来源**: transformers CONTRIBUTING.md 分析

---

## 一、核心要求

所有 vision-language 模型必须遵循以下规范才能合并到 transformers 主分支：

| 序号 | 要求 | 优先级 | 说明 |
|------|------|--------|------|
| 1 | Modular 架构 | ✅ 必须 | 所有代码在 modular_<model>.py 中 |
| 2 | Fast Image Processor | ✅ 必须 | 继承 BaseImageProcessorFast |
| 3 | 权重转换脚本 | ✅ 必须 | convert_<model>_to_hf.py |
| 4 | 集成测试 | ✅ 必须 | IntegrationTest 类 |
| 5 | 文档更新 | ✅ 必须 | model_doc/<model>.md |
| 6 | 质量检查 | ✅ 必须 | make style 通过 |

---

## 二、Modular 架构规范

### 2.1 必须创建 modular 文件

```bash
# 文件位置
src/transformers/models/<model_name>/modular_<model_name>.py

# 使用 CLI 生成骨架
transformers add-new-model-like

# 验证 modular 文件
python utils/modular_model_converter.py <model_name>
```

### 2.2 Modular 文件结构

```python
# modular_llava.py 示例

from transformers import (
    AutoConfig,
    AutoModel,
    AutoProcessor,
    AutoTokenizer,
    CLIPImageProcessor,
    LlamaTokenizer,
    PretrainedConfig,
)
from transformers.models.llava.configuration_llava import *
from transformers.models.llava.modeling_llava import *
from transformers.models.llava.processing_llava import *
from transformers.models.llava.image_processing_llava import *
from transformers.models.llava.tokenization_llava import *


class HunYuanVLConfig(PretrainedConfig):
    model_type = "hunyuan_vl"
    
    def __init__(self, ...):
        ...


@auto_docstring
class HunYuanVLModel(LlamaModel):
    ...


class HunYuanVLForConditionalGeneration(CausalLM):
    ...


class HunYuanVLProcessor(ProcessorMixin):
    ...
```

### 2.3 CI 强制要求

- **必须** 从 modular 文件生成 separate files
- **必须** 让 generated files 与 modular 文件匹配
- CI 会运行 `modular_model_converter.py` 验证

---

## 三、Fast Image Processor 规范

### 3.1 必须实现 Fast 版本

```python
from transformers import BaseImageProcessorFast

class HunYuanVLImageProcessorFast(BaseImageProcessorFast):
    """
    Fast image processor for HunYuanVL.
    Uses torch/torchvision instead of PIL/numpy.
    """
    pass
```

### 3.2 回退机制

```python
# 在 image_processing_auto.py 中
("hunyuan_vl", ("HunYuanVLImageProcessorFast", "HunYuanVLImageProcessor")),
```

- Fast 版本在前，slow 版本在后
- 如果 Fast 不可用，自动回退到 slow 版本

### 3.3 BaseImageProcessorFast 要求

- 必须使用 `torch` 和 `torchvision`
- 不使用 PIL/numpy
- 参考: [Issue #36978](https://github.com/huggingface/transformers/issues/36978)
- 示例: `LlavaOnevisionImageProcessorFast`, `Idefics2ImageProcessorFast`

---

## 四、权重转换脚本

### 4.1 必须创建转换脚本

```bash
# 文件位置
src/transformers/models/<model_name>/convert_<model_name>_to_hf.py
```

### 4.2 脚本结构

```python
"""
Convert <ModelName> checkpoint to HuggingFace format.
"""
import argparse
import torch
from transformers import AutoConfig, AutoModelForCausalLM

def convert_model_to_hf(original_model_path, output_path):
    """Convert model weights to HF format."""
    # 1. 加载原始模型
    original_model = load_original_model(original_model_path)
    
    # 2. 获取权重映射
    state_dict = original_model.state_dict()
    
    # 3. 转换权重键名
    converted_state_dict = {}
    for name, param in state_dict.items():
        hf_name = convert_key_name(name)
        converted_state_dict[hf_name] = param
    
    # 4. 加载 HF 配置
    config = AutoConfig.from_pretrained(original_model_path)
    hf_model = AutoModelForCausalLM.from_config(config)
    
    # 5. 加载权重并保存
    hf_model.load_state_dict(converted_state_dict)
    hf_model.save_pretrained(output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--original_model_path", type=str)
    parser.add_argument("--output_path", type=str)
    args = parser.parse_args()
    convert_model_to_hf(args.original_model_path, args.output_path)
```

### 4.3 参考示例

- `convert_llava_onevision_weights_to_hf.py`
- `convert_idefics2_weights_to_hf.py`

---

## 五、集成测试规范

### 5.1 必须添加 IntegrationTest

```python
# tests/models/<model_name>/test_modeling_<model_name>.py

import unittest
from transformers import AutoModelForConditionalGeneration, AutoProcessor
from transformers.testing_utils import slow


class HunYuanVLIntegrationTest(unittest.TestCase):
    @slow
    def test_model_integration(self):
        """Test end-to-end generation with exact output matching."""
        model_id = "tencent/HunyuanOCR"
        
        # 1. 加载模型和处理器
        model = AutoModelForConditionalGeneration.from_pretrained(model_id)
        processor = AutoProcessor.from_pretrained(model_id)
        
        # 2. 准备输入
        image = load_test_image()
        prompt = "Describe this image."
        inputs = processor(images=image, text=prompt, return_tensors="pt")
        
        # 3. 生成输出
        output = model.generate(**inputs, max_new_tokens=20)
        
        # 4. 验证输出
        EXPECTED_TEXT = "exact expected output"
        generated_text = processor.decode(output[0], skip_special_tokens=True)
        self.assertEqual(generated_text, EXPECTED_TEXT)
```

### 5.2 测试要求

- 使用真实检查点
- 生成模型：测试生成的文本是否匹配预期
- 非生成模型：测试输出的 logits 是否匹配预期值
- 参考示例: `tests/models/llava_onevision/test_modeling_llava_onevision.py`

---

## 六、文档规范

### 6.1 必须更新文档

```bash
# 文件位置
docs/source/en/model_doc/<model_name>.md
```

### 6.2 文档结构

```markdown
# HunYuanVL

## Overview

Brief description of the model.

## Usage examples

### Pipeline

```python
from transformers import pipeline

pipe = pipeline("image-text-to-text", model="tencent/HunyuanOCR")
```

### AutoModel

```python
from transformers import AutoModelForConditionalGeneration, AutoProcessor

model = AutoModelForConditionalGeneration.from_pretrained("tencent/HunyuanOCR")
processor = AutoProcessor.from_pretrained("tencent/HunyuanOCR")
```

## Resources

- [Paper link](url)
- [Hugging Face model](url)
```

---

## 七、质量检查

### 7.1 运行检查

```bash
# 安装质量依赖
pip install -e ".[quality]"

# 格式化代码
make style

# 检查仓库
make check-repo
```

### 7.2 检查内容

- `black` 格式化
- `ruff` linting
- 导入一致性
- docstring 完整性
- 代码规范

### 7.3 Google Style Docstring

```python
def example_function(arg1: int, arg2: str) -> bool:
    """Short description of the function.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Description of return value.

    Raises:
        ValueError: Description of when this error is raised.
    """
    pass
```

---

## 八、参考模型

| 模型 | 参考价值 |
|------|----------|
| LLaVA | 基础 vision-language 模式 |
| Idefics2 | Fast processor 示例 |
| Fuyu | 简单 vision-language 模式 |
| LLaVA-OneVision | 最新最佳实践 |

---

## 九、当前 HunyuanVL 状态

### 已完成 ✅
- [x] 代码迁移
- [x] 修复代码问题
- [x] 注册 Auto 类
- [x] 基础推理测试

### 待完成 ⏳
- [ ] 恢复 modular 架构
- [ ] 验证 modular 文件
- [ ] 实现 Fast Image Processor
- [ ] 创建权重转换脚本
- [ ] 添加集成测试
- [ ] 更新文档
- [ ] 运行 quality checks

---

## 十、命令速查

```bash
# 验证 modular 文件
python utils/modular_model_converter.py hunyuan_vl

# 运行样式检查
make style

# 运行完整检查
make check-repo

# 运行集成测试
python -m pytest tests/models/hunyuan_vl/test_modeling_hunyuan_vl.py -v
```

---

*最后更新: 2026-02-02 12:35*
*参考: transformers/CONTRIBUTING.md*
