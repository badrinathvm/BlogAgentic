from src.state.blogstate import BlogState, Blog
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.llms import HuggingFaceHub
import os

class BlogNode:
    """
    A class to represent a blog node.
    """

    def __init__(self, llm):
        self.llm = llm

    def transcript_extractor(self, state: BlogState):
        """
        Extract the transcript from the youtube links.
        """
        try:
            url = state["url"]
            loader = YoutubeLoader.from_youtube_url(youtube_url=url, add_video_info=False, language=["hi"],translation="en")
            documents = loader.load()
            return {"blog": {"transcript": documents[0].page_content}}
        except Exception as e:
            raise ValueError(f"Error Occurred with exception: {e}")
    

    def title_creation(self, state: BlogState):
        """
        Create a title for the blog.
        """
        if "url" in state and state["url"]:
            prompt = """You are expert blog writer. Use Markdown formatting.
                    Generate a single line blog title based on the {transcript}"""
            system_message = prompt.format(transcript=state['blog']['transcript'])
            llm_with_structured = self.llm.with_structured_output(Blog)
            response = llm_with_structured.invoke(system_message)
            return {"blog": response}
        
        elif "topic" in state and state["topic"]:
            prompt = """You are expert blog writer. Use Markdown formatting.
                    Generate a blog title only for the {topic}"""
            system_message = prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            return {"blog": {"title": response.content}}
        
        else:
         raise ValueError("Neither 'url' nor 'topic' is present in the state.")
    
    def content_generator(self, state: BlogState):
        """
        Generate content for the blog.
        """
        if "url" in state and state["url"]:
            system_prompt = """You are expert blog writer. Use Markdown formatting.
            Generate a blog content for the {transcript}"""
            system_message = system_prompt.format(transcript=state['blog'].transcript)
            llm_with_structured = self.llm.with_structured_output(Blog)
            response = llm_with_structured.invoke(system_message)
            return {"blog": response }
        
        elif "topic" in state and state["topic"]:
            system_prompt = """You are expert blog writer. Use Markdown formatting.
            Generate a blog contennt for the {topic}"""
            system_message = system_prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            return {"blog": {"title": state['blog']['title'], "content": response.content}}
            
        else:
         raise ValueError("Neither 'url' nor 'topic' is present in the state.")
        
    def route(self, state: BlogState):
        return {"current_language": state['current_language'] }
        
    def route_decision(self, state: BlogState):
        """
        Route the content to the respective translation function.
        """
        if state["current_language"] == "hindi":
            return "hindi"
        elif state["current_language"] == "french": 
            return "french"
        else:
            raise ValueError("Unsupported language specified.")

        
    def translation(self, state: BlogState):
        """
        Translate the content to the specified language.
        """
        translation_prompt = """
        Translate the following content into {current_language}.
        - Maintain the original tone, style, and formatting.
        - Adapt cultural references and idioms to be appropriate for {current_language}.

        ORIGINAL CONTENT:
        {blog_content}
        """
        blog_content = state["blog"]['content']
        messages = [
            HumanMessage(translation_prompt.format(current_language=state["current_language"], blog_content=blog_content))
        ]
        transaltion_content = self.llm.with_structured_output(Blog).invoke(messages)
        return {"blog": {"content": transaltion_content}}