# AI-Guided SOP Audit System

临床试验现场稽查引导系统 MVP。

## 功能

- 流程树：准备、研究者文件夹、知情同意、入排标准、访视、AE/SAE、EDC一致性、问题汇总
- 任务卡：提示当前步骤、需查看资料、需填写字段、判断标准
- 规则判断：日期时序、版本、授权培训、源文件与EDC一致性
- 自动生成：稽查发现记录、补充证据提示、CSV问题清单、Word报告初稿

## 运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 后续扩展

可继续接入 OCR、LLM、知识库、数据库、账号权限和CAPA闭环。
