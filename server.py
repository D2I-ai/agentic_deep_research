import json
import os
import uvicorn
from threading import Lock
from typing import List
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent.deep_research_demo import DeepResearch
from tools.file_parse import handle_file_name, loadJson

from _setting import LLM_MODEL_NAME

app = FastAPI()
index_lock = Lock()


class History(BaseModel):
    user: str
    bot: str


class DeepResearchItem(BaseModel):
    input: str
    model_name: str | None = LLM_MODEL_NAME
    history: List[History] = Field(default_factory=list)
    stream: bool
    increase: bool


class ThinkingStatusResponse(BaseModel):
    topic: str
    userid: str


@app.post("/deepresearch/thinking/status")
def get_thinking_status(response: ThinkingStatusResponse):
    topic = handle_file_name(response.topic)
    json_array = loadJson(f"data/thinking_status/{topic}.json")

    # 线程安全操作索引 ｜ Thread-safe file reading
    with index_lock:
        with open("data/thinking_status/status.json", "r", encoding="utf-8") as status:
            current_indices = json.loads(status.read())
        # 获取当前索引（不存在则初始化为0）
        current_index = current_indices.get(topic, 0)

        if current_index >= len(json_array):
            current_index = len(json_array) - 1
        # 更新索引（+1后存储）｜ Update the index
        element = json_array[current_index]
        current_indices[topic] = current_index + 1
        with open("data/thinking_status/status.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(current_indices, ensure_ascii=False))
    return {"code": "200", "msg": "success", "request_id": "123456789", "data": element}


@app.post("/deepresearch/agent/chat")
async def deepresearch_agent(deepresearch: DeepResearchItem):
    input_query = deepresearch.input
    model_name = deepresearch.model_name
    stream = deepresearch.stream
    with open("data/thinking_status/status.json", "r", encoding="utf-8") as rf:
        status_json = json.loads(rf.read())
    status_json[input_query] = 0
    with open("data/thinking_status/status.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(status_json, ensure_ascii=False))
    if model_name == "":
        deep_research = DeepResearch(input_query, model = LLM_MODEL_NAME, stream=stream)
    else:
        deep_research = DeepResearch(input_query, model = model_name, stream=stream)
    answer = await deep_research.inference()
    if not deep_research.stream_mode:
        answer = json.dumps(
            {
                "code": "200",
                "msg": "success",
                "request_id": "123456789",
                "data": deep_research.final_answer,
            }
        )

    return StreamingResponse(answer, media_type="application/octet-stream")


# 如果data/status/下没有status.json文件创建一个
# Create a status.json file under data/status/ if it does not already exist.
if not os.path.exists("data/thinking_status/status.json"):
    os.makedirs("data/thinking_status", exist_ok=True)
    with open("data/thinking_status/status.json", "w", encoding="utf-8") as f:
        f.write("{}")

if __name__ == "__main__":
    uvicorn.run(app="server:app", host="0.0.0.0", port=3456, workers=8)
