Template for creating and submitting MAT496 capstone project.

# Overview of MAT496

In this course, we have primarily learned Langgraph. This is helpful tool to build apps which can process unstructured `text`, find information we are looking for, and present the format we choose. Some specific topics we have covered are:

- Prompting
- Structured Output 
- Semantic Search
- Retreaval Augmented Generation (RAG)
- Tool calling LLMs & MCP
- Langgraph: State, Nodes, Graph

We also learned that Langsmith is a nice tool for debugging Langgraph codes.

------

# Capstone Project objective

The first purpose of the capstone project is to give a chance to revise all the major above listed topics. The second purpose of the capstone is to show your creativity. Think about all the problems which you can not have solved earlier, but are not possible to solve with the concepts learned in this course. For example, We can use LLM to analyse all kinds of news: sports news, financial news, political news. Another example, we can use LLMs to build a legal assistant. Pretty much anything which requires lots of reading, can be outsourced to LLMs. Let your imagination run free.


-------------------------

# Project report Template

## Title: NBA Roster & Injury Status Assistant using LangGraph and RAG

## Overview

My project builds an LLM-powered assistant that tracks NBA rosters and player injury statuses (Out / Day-to-day / Healthy). It automatically fetches roster and injury data, stores structured summaries, and lets users ask natural-language questions like ‘Who is out for the Lakers tonight and why?’ The system uses LangGraph to orchestrate tools, semantic search, and RAG to generate updated, human-readable responses.

## Reason for picking up this project

Real-world use case of LLMs processing constantly changing text-heavy information like injury reports and news. I also was doing another project to predict player stats for his next game based on previous data and having this would help me. Also I like basketball.

## Plan

I plan to excecute these steps to complete my project.

- [TODO] Step 1 Defining data source, where will i get/scrape from
- [TODO] Step 2 Creating the necessary tool functions for getting team roster, getting team/player status and updating an excel sheet.
- [TODO] Step 3 Defining structure output schemas with what we need to save and answer
- [TODO] Step 4 Collect short text about why the player is injured
- [TODO] Step 5 Create Langgraph state with data you want persisted across nodes and building them
- [TODO] Step 6 Connecting and making the langgraph flow
- [TODO] Step 7 Test using Langsmith

## Conclusion:

I had planned to achieve {this this}. I think I have/have-not achieved the conclusion satisfactorily. The reason for your satisfaction/unsatisfaction.

----------

# Added instructions:

- This is a `solo assignment`. Each of you will work alone. You are free to talk, discuss with chatgpt, but you are responsible for what you submit. Some students may be called for viva. You should be able to each and every line of work submitted by you.

- `commit` History maintenance.
  - Fork this respository and build on top of that.
  - For every step in your plan, there has to be a commit.
  - Change [TODO] to [DONE] in the plan, before you commit after that step. 
  - The commit history should show decent amount of work spread into minimum two dates. 
  - **All the commits done in one day will be rejected**. Even if you are capable of doing the whole thing in one day, refine it in two days.  
 
 - Deadline: Nov 30, Sunday 11:59 pm


# Grading: total 25 marks

- Coverage of most of topics in this class: 20
- Creativity: 5
  
