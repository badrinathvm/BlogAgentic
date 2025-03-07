import uvicorn
from fastapi import FastAPI, Request
from src.graph.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM

from langgraph.graph import StateGraph, START, END
from src.state.blogstate import BlogState

app = FastAPI()

@app.post("/blog")
async def create_blog(request: Request):
    data = await request.json()
    topic = data.get("topic", "")
    youtube_url = data.get("url", "")
    language = data.get("language", '')

    # Get the llm object 
    llm = GroqLLM().get_llm()

    # get the graph 
    graph_builder = GraphBuilder(llm)
    
    if topic and language:
         graph = graph_builder.set_up_graph(usecase="language")
         state = graph.invoke({"topic": topic, "current_language": language.lower()})
    elif youtube_url:
        graph = graph_builder.set_up_graph(usecase="url")
        state = graph.invoke({"url": youtube_url})
    elif topic:
         graph = graph_builder.set_up_graph(usecase="topic")
         state = graph.invoke({"topic": topic})
    else:
        return {"error": "No valid input provided"}
    return {"data": state }

if __name__ == "__main__":
    uvicorn.run("blog:app", host="0.0.0.0", port=8001, reload=True)