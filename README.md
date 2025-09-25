<div align="center">
  <h1>A Strong Baseline of Agentic Deep Research</h1>
  <p><strong>A simple, powerful, and extensible framework for agentic deep research using LLMs</strong></p>

  ![GitHub Deployments](https://img.shields.io/github/deployments/u14app/gemini-next-chat/Production)
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![GitHub stars](https://img.shields.io/github/stars/D2I-ai/agentic_deep_research?style=social)](https://github.com/D2I-ai/agentic_deep_research)

</div>

## 🌟 Overview

This project provides a lightweight yet powerful agentic framework designed to enable **multi-hop web search** and **automated deep research report generation** using the function-calling capabilities of LLMs. It empowers developers and researchers to build autonomous agents that can search, reason, and synthesize information from the web with minimal setup.

Whether you're building a research assistant, competitive intelligence tool, or knowledge curation system, this project provides a clean, modular, and easy-to-extend foundation.

## 🎥 Demo

<p align="center">
  <img src="./assets/deepresearch_demo_en.gif" width="400" alt="deepresearch demo 1" />
  <img src="./assets/deepresearch_demo_zh.gif" width="400" alt="deepresearch demo 2" />
</p>

## 🔧 Key Features

- ✅ **Easy-to-Use** - Simple interface for multi-hop search and report generation — get started in minutes.

- 🔍 **Multi-Hop Web Search** - Agents perform iterative searches to gather comprehensive information across multiple sources.

- 🌐 **Multiple Search Tools Supported** - Choose from Serper, Jina, Tavily, Firecrawl, and more — plug in your preferred search engine.

- 🧠 **LLM Agnostic** - Supports various LLMs via API (e.g., Qwen, GPT-4o) through the DashScope or OpenAI-compatible interface.

- 📈 **Built-in Evaluation Pipeline** - Evaluate performance on multi-hop QA and report generation tasks out-of-the-box.

- 🌍 **Multi-Language Support** - Fully supports both **English** and **简体中文**.

- 🖥️ **Local Deployment Ready** - Supports full-stack deployment (frontend + backend) in local or private environments for enhanced privacy and control.

- 📜 **MIT Licensed** - Open-source and free for personal and commercial use.


## 🚀 Quickstart

### 1. Use Dashscope API
Dashscope is a platform providing AI-powered APIs and tools for natural language processing, computer vision, and other machine learning tasks. You can get the LLM API from Dashscope.
1. [Dashscope Uasge](https://github.com/dashscope/dashscope-sdk-python)
2. [Get Your API Key](https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api?spm=a2c4g.11186623.0.0.46197d9dC7SfoW) ｜ [获取您的 API Key](https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api?spm=a2c4g.11186623.0.0.46197d9dC7SfoW)
3. Put your API key in `_settings.py`


### 2. Websearch Tools
Websearch tools are used to perform websearch and retrieve webpages for deep research.

#### Get Your search API Key
We support the following websearch tools:
- [Serper](https://serper.dev/)
- [Jina](https://jina.ai/)
- [Tavily](https://tavily.com/)
- [Firecrawl](https://firecrawl.ai/)

You can set search backend in `_settings.py`:
```python
WEBSEARCH_API = ("jina")  # or "tavily", "firecrawl", "local_jina", "custom"
```

💡 Tips: 
1. We recommend [Jina](https://jina.ai/) for its cost-efficiency and excellent content extraction. You can deploy [Jina Read](https://github.com/jina-ai/reader) locally for full control. 
2. If you want to choose serper_api, you need to set the WEBSEARCH_API to `custom`.


### 3. Installation and Configuration

#### 3.1 Clone the repository

   ```bash
   git clone https://github.com/D2I-ai/agentic_deep_research.git
   cd agentic_deep_research
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

#### 3.2 Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

#### 3.3 Set up your API keys
You need to edit the `_settings.py` file and provide your API key. You need to provide at least dashscope API key and one of the websearch API keys.
   ```python
    APIKeys = {
        "dashscope_api_key": "your dashscope api key",
        "serper_api": "your serper api key",
        "jina_api_key": "your jina api key",
        "tavily_api_key": "your tavily api key",
        "firecrawl_api_key": "your firecrawl api key"
    }
   ```

#### 3.4 Test Your LLM API
   ```python
    python agent/model.py
   ```

#### 3.5 Test the websearch tool
   ```python
   python websearch/query2text.py
   ```

### 4. Run the deep search pipeline

Launch the full agentic pipeline:
```python
python agent/deep_research_demo.py
```

## 📊 Performance Benchmarks

Our agentic deep research achieve strong results on multi-hop QA and report generation tasks. Below are accuracy scores on public benchmarks (↑ is better):

| **Models**                  | **HotpotQA_dev_subset** | **Musique_test_subset** | **Bamboogle** |
|:----------------------------------:|:-----------------------:|:-----------------------:|:-------------:|
| qwen2.5-7b                         | 30.00%                  | 13.00%                  | 36.00%        |
| qwen2.5-max                        | 60.00%                  | 25.00%                  | 74.40%        |
| qwen3-235b-a22b                    | 53.30%                  | 25.00%                  | 66.40%        |
| gpt-4o-0806                        | 66.70%                  | 36.00%                  | 76.80%        |
| DeepSeek-R1-0528                   | 53.30%                  | 34.00%                  | 78.40%        |
| Search-R1<br>（Local RAG） *        | 63.00%                  | 27.50%                  | 57.60%        |
| R1-Searcher *                      | 53.10%                  | 25.60%                  | 65.60%        |
| DeepResearcher *                   | 64.30%                  | 29.30%                  | 72.80%        |
| Ours<br>（qwen2.5-7b-instruct） | 70.00%                  | 29.00%                  | 64.80%        |
| <b>Ours<br>（qwen2.5-max）</b> | <b>83.30%</b>           | <b>41.00%</b>           | 78.40%        |
| Ours<br>（qwen3-235b-a22b）     | 80.00%                  | 36.00%                  | <b>84.00%</b> |

## 🧪 Auto Evaluation

Evaluate your agent’s performance using our built-in pipeline:

```python
python evaluation/eval_deepresearch.py
```

## 📋 Roadmap (TODO)

- [ ] Add support for MCP.
- [ ] Add support for more evaluation benchmarks, such as GAIA.
- [ ] Add more finegrained tools.
- [ ] Provide docker image for easy deployment.
- [ ] Release an agent RL training dataset 10K+ samples.

## ⚙️ Development

### 1. Backend development
  Launch the backend server:
  ```python
  python server.py
  ```

### 2. Frontend development
  Following the [web/README-EN.md](./web/README-EN.md) | [web/README-ZH.md](./web/README-ZH.md) to launch the frontend server

## 🙏 Acknowledgements

We thank the following projects for inspiration and foundational tools:

- [Qwen Agent](https://github.com/QwenLM/Qwen-Agent) - Qwen agent is a powerful LLM agent that provides a simple and intuitive interface for users to implement different agent systems.
- [Jina Read](https://github.com/jina-ai/reader) - Jina read provides a simple and efficient way to extract text from given urls.


## 🌟 Misc

<div align="center">
[![Star History Chart](https://api.star-history.com/svg?repos=D2I-ai/agentic_deep_research&type=Date)](https://star-history.com/#D2I-ai/agentic_deep_research&Date)


</div>


## 📝 License

This project is released under the [MIT License](LICENSE). This license allows for free use, modification, and distribution for both commercial and non-commercial purposes.

## 🌟 Cite Us

If you use this project in your research, please cite:


```tex
@misc{SADR,
      title={A Strong Baseline of Agentic Deep Research},
      author={Chao Chen, Zhihang Fu, Ze Chen},
}
```


<div align="center">
<p><em>Made with ❤️ for the open-source community</em></p>
<p>
<a href="https://github.com/D2I-ai/agentic_deep_research">View on GitHub</a> •
<a href="https://github.com/D2I-ai/agentic_deep_research/stargazers">Star Us</a>
</p>
</div>
