from dotenv import load_dotenv
import streamlit as st 
import os
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from data_ingestion import extract_page_text ,get_docs
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel ,Field
from typing import Annotated ,TypedDict , Literal
from collections import Counter
import matplotlib.pyplot as plt
from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
class structured_output(BaseModel):
	summary : str = Field(... , description = "Summary of the model")
	sentiment :  Literal["positive" , "negative" , "mixed"] = Field(... , description = "Sentiment of the text")

parser = PydanticOutputParser(pydantic_object=structured_output)
load_dotenv()
st.title("Company review")
def agent():

	llm = HuggingFaceEndpoint(repo_id ="google/gemma-4-31B-it" , task = "text_generation" , temperature = 0.5)
	model = ChatHuggingFace(llm = llm)
	#now lets get the company of which you want the review 

	company_name = st.text_input("Enter the company name you want to get the review ")

	prompt = PromptTemplate(
    template="""
    Analyze the following company review text.

    1. Summarize the key information in 3-4 lines.
    2. Determine its overall sentiment.

    Review text:
    {input_text}
    """,
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

	chain = prompt | model | parser
	
	if st.button("Analyze company"):
		with st.spinner("Searching the web ...... "):
			page_docs= get_docs(company_name)
			#now we get the page content for the model 
			if not page_docs:
				st.warning("No results found for the company")
			page_content_docs = extract_page_text(page_docs)
			if page_content_docs:
				st.write(f"Extracted {len(page_content_docs)} documents from the web")
			sentiment_list = []

			#now we will print a summary for all the pages 
			for index , documents in enumerate(page_content_docs):
				st.write(page_content_docs[index]['text'][:200])
				st.caption(page_content_docs[index]['url'])
				st.write("------------------------------")

			
			for index , documents in enumerate(page_content_docs):
				result = chain.invoke({'input_text' : documents[:1000]})
				st.write(result.summary)
				st.write(f"Sentiment : {result.sentiment}")
				sentiment_list.append(result.sentiment)
				st.caption(f"{url_list[index]['url']}")
				st.write("---------------------------------------------------------------------------")
			
			#after getting the sentiments of all the documents
			st.title(f"Summary of {len(url_list)} documents")
			counts = Counter(sentiments)

			labels = list(counts.keys())
			values = list(counts.values())

			fig, ax = plt.subplots()

			ax.pie(
    			values,
    			labels=labels,
    			autopct="%1.1f%%",
   				startangle=90
				)

			ax.axis("equal")
			st.subheader("Company Review Sentiment Distribution")
			st.pyplot(fig)

	
			#so we have the company names , now lets get the url
			#here we will summarize each document 

agent()






