import asyncio
import json
import os
import re

from _setting import DEEPRESEARCH_OUTPUT_DIR, LLM_OUTPUT_DIR
from agent.deep_research_demo import DeepResearch
from agent.model import dashscope_openai_api
from evaluation.eval_prompt import EVAL_ANSWER_QUALITY, EVAL_CRITERION, EVAL_PROMPT_QA
from tools.file_parse import loadJson, save2Json


def extract_json_from_codeblock(text):
    """
    Extracts the content of the first ```json code block.
    Returns None if no such block is found.
    """
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None


# Evaluate the performance of general LLMs on multi-hop QA benchmarks, like HotpotQA and Musique.
def eval_llm_QA():
    # set model name
    eval_model_name = "qwen3-235b-a22b"

    # set dataset
    eval_data_name = "bamboogle_test"
    test_data_dict = {
        "hotpot_dev_subset": "data/deepresearch_eval_data/hotpot_dev_subset.json",
        "musique_test_subset": "data/deepresearch_eval_data/musique_test_subset.json",
        "bamboogle_test": "data/deepresearch_eval_data/bamboogle_test.json",
    }

    eval_dataset_path = test_data_dict[eval_data_name]
    eval_dataset = loadJson(eval_dataset_path)

    acc_count = 0
    total_count = 0
    for ind, item in enumerate(eval_dataset):
        try:
            question = item["question"]
            gt_answer = item["answer"]

            # get llm output
            llm_answer = dashscope_openai_api(prompt=question, model_name=eval_model_name)

            ## LLM-as-Judge Evaluation
            eval_prompt = EVAL_PROMPT_QA.format(
                question=question, gt_answer=gt_answer, llm_answer=llm_answer
            )
            llm_eval_res = dashscope_openai_api(
                eval_prompt, model_name="qwen-max-2025-01-25"
            )
            print("llm_eval_res: ", llm_eval_res)

            if "true" in llm_eval_res.lower():
                acc_count += 1
            total_count += 1
        except:
            pass
    print(f"Acc count: {acc_count}")
    print(f"Total count: {total_count}")
    print(f"Acc: {1.0*acc_count/total_count}")


# Evaluate the performance of DeepResearch system on multi-hop QA benchmarks.
def eval_deepresearch_QA():
    test_data_dict = {
        "hotpot_dev_subset": "data/deepresearch_eval_data/hotpot_dev_subset.json",
        "musique_test_subset": "data/deepresearch_eval_data/musique_test_subset.json",
        "bamboogle_test": "data/deepresearch_eval_data/bamboogle_test.json",
    }

    test_model_name = "qwen-max-2025-01-25"
    test_data_list = ["hotpot_dev_subset", "musique_test_subset", "bamboogle_test"]
    for test_data_name in test_data_list:
        test_data_path = test_data_dict[test_data_name]
        test_data = loadJson(test_data_path)
        result_data = []
        acc_count = 0
        total_count = 0
        for ind, item in enumerate(test_data):
            question = item["question"]
            gt_answer = item["answer"]
            print(question)
            try:
                deep_research = DeepResearch(input_query=question, model=test_model_name)
                deepresearch_answer = asyncio.run(deep_research.inference())
                item["llm_answer"] = deepresearch_answer

                eval_prompt = EVAL_PROMPT_QA.format(
                    question=question, gt_answer=gt_answer, llm_answer=deepresearch_answer
                )
                llm_eval_res = dashscope_openai_api(
                    eval_prompt, model_name="qwen-max-2025-01-25"
                )

                if "true" in llm_eval_res.lower():
                    acc_count += 1
                    item["llm_eval_result"] = 1
                else:
                    item["llm_eval_result"] = 0

                result_data.append(item)
                total_count += 1
            except:
                pass

            if ind % 1 == 0:
                save2Json(
                    result_data,
                    DEEPRESEARCH_OUTPUT_DIR / f"000-{test_data_name}-{test_model_name}.json",
                )

        print(f"Acc count: {acc_count}")
        print(f"Total count: {total_count}")
        print(f"Acc: {1.0*acc_count/total_count}")
        save2Json(
            result_data,
            DEEPRESEARCH_OUTPUT_DIR / f"000-{test_data_name}-{test_model_name}.json",
        )


# Evaluate the performance of DeepResearch system on Researchy benchmarks.
def eval_deepresearch_report():
    researchy_test_subset = loadJson(
        "data/deepresearch_eval_data/researchy_test_subset.json"
    )

    test_data_name = "researchy"
    test_model_name = "qwen2.5-7b-instruct"
    eval_mode = "DeepResearch"  # "LLM" or "DeepResearch"

    valid_count = 0
    (
        total_clarity_score,
        total_insightfulness_score,
        total_depth_score,
        total_breadth_score,
    ) = (0, 0, 0, 0)
    result_data = []
    for ind, item in enumerate(researchy_test_subset):
        try:
            question = item["question"]
            # get deep research result
            if eval_mode == "DeepResearch":
                deep_research = DeepResearch(input_query=question, model=test_model_name)
                answer = asyncio.run(deep_research.inference())

            # get llm results
            elif eval_mode == "LLM":
                answer = dashscope_openai_api(prompt=question, model_name=test_model_name)
            else:
                print("error eval_mode")
                exit()

            (
                clarity_eval_score,
                insightfulness_eval_score,
                depth_eval_scroe,
                breadth_eval_scroe,
            ) = get_llm_rating(question, answer)

            item["deepresearch_answer"] = answer
            item["clarity_score"] = clarity_eval_score
            item["insightfulness_score"] = insightfulness_eval_score
            item["depth_eval_scroe"] = depth_eval_scroe
            item["breadth_eval_scroe"] = breadth_eval_scroe

            valid_count += 1
            total_clarity_score += clarity_eval_score
            total_insightfulness_score += insightfulness_eval_score
            total_depth_score += depth_eval_scroe
            total_breadth_score += breadth_eval_scroe
            result_data.append(item)
        except:
            pass

        if ind % 3 == 0:
            if eval_mode == "DeepResearch":
                save2Json(
                    result_data,
                    DEEPRESEARCH_OUTPUT_DIR / f"000-{test_data_name}-{test_model_name}.json",
                )
            elif eval_mode == "LLM":
                save2Json(
                    result_data,
                    LLM_OUTPUT_DIR / f"000-{test_data_name}-{test_model_name}.json",
                )
    print(f"Valid count: {valid_count}")
    print(f"Avg clarity: {1.0*total_clarity_score/valid_count}")
    print(f"Avg insightfulness: {1.0*total_insightfulness_score/valid_count}")
    print(f"Avg depth: {1.0*total_depth_score/valid_count}")
    print(f"Avg breadth: {1.0*total_breadth_score/valid_count}")
    if eval_mode == "DeepResearch":
        save2Json(
            result_data,
            DEEPRESEARCH_OUTPUT_DIR / f"000-{test_data_name}-{test_model_name}.json",
        )
    elif eval_mode == "LLM":
        save2Json(
            result_data, LLM_OUTPUT_DIR / f"000-{test_data_name}-{test_model_name}.json"
        )


# use LLM-as-Judge for report rating
def get_llm_rating(question, answer):
    # Clarity evaluation
    clarity_eval_prompt = EVAL_ANSWER_QUALITY.format(
        criterion_name="Clarity",
        criterion_desc=EVAL_CRITERION["Clarity"],
        question=question,
        answer=answer,
    )
    clarity_eval_result = dashscope_openai_api(
        prompt=clarity_eval_prompt, model_name="qwen-max-2025-01-25"
    )
    clarity_eval_result = extract_json_from_codeblock(clarity_eval_result)
    clarity_eval_result = json.loads(clarity_eval_result)
    clarity_eval_score = clarity_eval_result["rating"]
    print("clarity_eval_score:", clarity_eval_score)

    # Insightfulness evaluation
    insightfulness_eval_prompt = EVAL_ANSWER_QUALITY.format(
        criterion_name="Insightfulness",
        criterion_desc=EVAL_CRITERION["Insightfulness"],
        question=question,
        answer=answer,
    )
    insightfulness_eval_result = dashscope_openai_api(
        prompt=insightfulness_eval_prompt, model_name="qwen-max-2025-01-25"
    )
    insightfulness_eval_result = extract_json_from_codeblock(insightfulness_eval_result)
    insightfulness_eval_result = json.loads(insightfulness_eval_result)
    insightfulness_eval_score = insightfulness_eval_result["rating"]
    print("insightfulness_eval_score:", insightfulness_eval_score)

    # Depth evaluation
    depth_eval_prompt = EVAL_ANSWER_QUALITY.format(
        criterion_name="Depth",
        criterion_desc=EVAL_CRITERION["Depth"],
        question=question,
        answer=answer,
    )
    depth_eval_result = dashscope_openai_api(
        prompt=depth_eval_prompt, model_name="qwen-max-2025-01-25"
    )
    depth_eval_result = extract_json_from_codeblock(depth_eval_result)
    depth_eval_result = json.loads(depth_eval_result)
    depth_eval_scroe = depth_eval_result["rating"]
    print("depth_eval_scroe:", depth_eval_scroe)

    # Breadth evaluation
    breadth_eval_prompt = EVAL_ANSWER_QUALITY.format(
        criterion_name="Breadth",
        criterion_desc=EVAL_CRITERION["Breadth"],
        question=question,
        answer=answer,
    )
    breadth_eval_result = dashscope_openai_api(
        prompt=breadth_eval_prompt, model_name="qwen-max-2025-01-25"
    )
    breadth_eval_result = extract_json_from_codeblock(breadth_eval_result)
    breadth_eval_result = json.loads(breadth_eval_result)
    breadth_eval_scroe = breadth_eval_result["rating"]
    print("breadth_eval_scroe:", breadth_eval_scroe)
    return (
        clarity_eval_score,
        insightfulness_eval_score,
        depth_eval_scroe,
        breadth_eval_scroe,
    )


if __name__ == "__main__":
    # eval_llm_QA()
    eval_deepresearch_QA()
    # eval_deepresearch_report()
