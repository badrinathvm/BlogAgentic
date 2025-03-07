from langgraph.graph import StateGraph, START, END
from src.llms.groqllm import GroqLLM
from src.nodes.blog_node import BlogNode
from src.state.blogstate import BlogState

class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm
        self.graph = StateGraph(BlogState)

    def build_url_graph(self):
        """
        Build a graph from the given llm.
        """
        self.blog_node = BlogNode(self.llm)
        self.graph.add_node("transcript_extractor", self.blog_node.transcript_extractor)
        self.graph.add_node("title_creation", self.blog_node.title_creation)
        self.graph.add_node("content_generator", self.blog_node.content_generator)

        self.graph.add_edge(START, "transcript_extractor")
        self.graph.add_edge("transcript_extractor", "title_creation")
        self.graph.add_edge("title_creation", "content_generator")
        self.graph.add_edge("content_generator", END)

        return self.graph
    
    def build_topic_graph(self):
        """
        Build a graph from the given llm.
        """
        self.blog_node = BlogNode(self.llm)
        # Nodes
        self.graph.add_node("title_creation", self.blog_node.title_creation)
        self.graph.add_node("content_generator", self.blog_node.content_generator)

        # Edges
        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generator")
        self.graph.add_edge("content_generator", END)

        return self.graph
    
    def build_multi_language_graph(self):
        """
        Build a graph from that converts the blog content to multiple languages.
        """
        self.blog_node = BlogNode(self.llm)
        
        # Nodes
        self.graph.add_node("title_creation", self.blog_node.title_creation)
        self.graph.add_node("content_generator", self.blog_node.content_generator)
        self.graph.add_node("hindi_translation", lambda state: self.blog_node.translation({**state, "current_language": "hindi"}))
        self.graph.add_node("french_translation", lambda state: self.blog_node.translation({**state, "current_language": "french"}))

        # Routing Node
        self.graph.add_node("route", self.blog_node.route)

        #edges
        self.graph.add_edge(START, "title_creation")
        self.graph.add_edge("title_creation", "content_generator")
        self.graph.add_edge("content_generator", "route")

        # conditional edges 
        self.graph.add_conditional_edges(
            "route",
            self.blog_node.route_decision,
            {
                "hindi": "hindi_translation",
                "french": "french_translation"
            }
        )
        self.graph.add_edge("hindi_translation", END)
        self.graph.add_edge("french_translation", END)
        return self.graph

    
    def set_up_graph(self, usecase):
        """
        Set up the graph based on the usecase.
        """
        if usecase == "url":
            self.build_url_graph()
        if usecase == "topic":
            self.build_topic_graph()
        if usecase == "language":
            self.build_multi_language_graph()
        return self.graph.compile()
    
# Below code is for langsmith decode    
# llm = GroqLLM().get_llm()

# # get the graph 
# graph_builder = GraphBuilder(llm)
# graph = graph_builder.build_topic_graph().compile()