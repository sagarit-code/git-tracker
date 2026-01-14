
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
import os
from dotenv import load_dotenv
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#model setup
load_dotenv()



METRICS_FILE = "metrics_history.json"

#loading
def load_previous_metrics():
    if not os.path.exists(METRICS_FILE):
        return None

    with open(METRICS_FILE, "r") as f:
        try:
            data = json.load(f)
            return data if data else None
        except json.JSONDecodeError:
            return None


def save_current_metrics(metrics: dict):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)


model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

#keys setup
SMTP_HOST=os.getenv("SMTP_HOST")
SMTP_PORT=int(os.getenv("SMTP_PORT"))
SMTP_USER=os.getenv("SMTP_USER")
SMTP_PASS=os.getenv("SMTP_PASS")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "langgraph-agent"
    }



#state of grpah setup
class Oldmetrics(TypedDict):
    views:int
    uni_view:int
    clone:int
    uni_clone:int
    stars:int

class Gitstate(TypedDict,total=False):
    repo_url:str
    view:int
    clones:int
    unique_clone:int
    stars:int
    unique_views:int
    previous_metrics:Oldmetrics
    summary_ans:str
    social_type:str
    post:str
    status:str


#nodes


def stars_checking(state:Gitstate) -> Gitstate:
    
    recieving_url=state["repo_url"]
    user=recieving_url.split("/")[-2]
    repo=recieving_url.split("/")[-1]

    url=f"https://api.github.com/repos/{user}/{repo}"
    response = requests.get(url, headers=headers)

    data = response.json()

    stars = data["stargazers_count"]
    
    state["stars"]=stars

    return state
    

def clones_checking(state:Gitstate) -> Gitstate:
    recieving_url=state["repo_url"]
    extracting_user=recieving_url.split("/")[-2]
    extracting_repo=recieving_url.split("/")[-1]

    traffic_url=f"https://api.github.com/repos/{extracting_user}/{extracting_repo}/traffic/clones"
    response=requests.get(url=traffic_url,headers=headers)
    response_json=response.json()

    clone=response_json["count"]
    unique_clone=response_json["uniques"]

    state["clones"]=clone
    state["unique_clone"]=unique_clone

    return state

def traffic_views(state:Gitstate) -> Gitstate:

    recieving_url=state["repo_url"]
    extracting_user=recieving_url.split("/")[-2]
    extracting_repo=recieving_url.split("/")[-1]

    traffic_url=f"https://api.github.com/repos/{extracting_user}/{extracting_repo}/traffic/views"
    response=requests.get(url=traffic_url,headers=headers)
    response_json=response.json()
    
    view=response_json["count"]
    unique_view=response_json["uniques"]

    state["view"]=view
    state["unique_views"]=unique_view

    return state

def llm_summary(state:Gitstate) -> Gitstate:
    llm_input = {
    "previous_period": state.get("previous_metrics", {
    "stars": 0,
    "views": 0,
    "uni_view": 0,
    "clone": 0,
    "uni_clone": 0}),

    "current_period": {
        "stars": state["stars"],
        "views": state["view"],
        "unique_visitors": state["unique_views"],
        "clones": state["clones"],
        "unique_cloners": state["unique_clone"],
        
    }
}

    prompt=f''''

    You are a technical growth analyst for open-source projects.

You are given two snapshots of GitHub repository analytics both in dictionaries format:
1) previous_period (earlier 24h window)-{llm_input["previous_period"]}

2) current_period (latest 24h window)-{llm_input["current_period"]}

Your job is to:
- compute differences
- interpret trends
- explain what changed and why it matters
- give practical next steps

INPUT DATA:
- Repository name
- previous_period:
  - stars
  - views
  - unique_visitors
  - clones
  - unique_cloners
- current_period:
  - stars
  - views
  - unique_visitors
  - clones
  - unique_cloners
- optional:
  - top_referrers
  - popular_paths

RULES:
- Always compare current_period vs previous_period
- Calculate absolute and percentage change where meaningful
- If a metric is unchanged, say so explicitly
- Never invent causes — infer cautiously from the data
- If data is missing, acknowledge it

ANALYSIS GUIDELINES:
- Rising stars → interest or social exposure
- Rising views but flat stars → awareness without conversion
- Rising clones → strong developer intent
- Falling metrics → reduced visibility or inactivity

OUTPUT STRUCTURE:

Overall Summary:
<1–2 lines describing momentum: growing / flat / declining>

Metric Breakdown:
- ⭐ Stars:
  - Previous: X → Current: Y
  - Change: +/- N (±%)
  - Interpretation
- 👀 Traffic:
  - Previous: X views (U uniques)
  - Current: Y views (V uniques)
  - Change and interpretation
- 📥 Clones:
  - Previous: X (U uniques)
  - Current: Y (V uniques)
  - Change and interpretation

Key Insights:
- <insight 1>
- <insight 2>

Recommended Actions (doable in next 24h):
1. <specific action>
2. <specific action>
3. <optional action>

TONE:
- Clear, precise, founder-to-founder
- Analytical, not marketing
- No emojis
- No fluff'''
    response=model.invoke(prompt)
    answer=response.content
    state["summary_ans"]=answer
    return state


def persist_metrics(state: Gitstate) -> Gitstate:
    current_metrics = {
        "stars": state["stars"],
        "views": state["view"],
        "uni_view": state["unique_views"],
        "clone": state["clones"],
        "uni_clone": state["unique_clone"]
    }

    save_current_metrics(current_metrics)
    return state


def generating_linkedin_post(state:Gitstate) -> Gitstate:
    prompt=f'''
You are a professional technical writer and founder building in public.

You are given a concise analytics summary about a GitHub repository’s performance over the last 24 hours.

Your task is to convert this summary into a polished, professional LinkedIn post that:
- Sounds thoughtful and credible
- Uses short paragraphs and clean spacing
- Explains progress without bragging
- Reflects learning, iteration, and momentum
- Is suitable for founders, engineers, and product leaders

INPUT:
{state["summary_ans"]}

GUIDELINES:
- Write in first person (“I” / “we”)
- Keep the tone calm, reflective, and professional
- No emojis
- No hype phrases like “game changer”, “insane growth”, “crushing it”
- No hashtags spam (max 2–3 at the end)
- Do not invent metrics; use only what is in the summary
- Avoid sounding like marketing copy

STRUCTURE:
1. Opening paragraph: context (what you’re building / observing)
2. Middle paragraphs:
   - What changed
   - What it signals about users or developers
3. Closing paragraph:
   - A takeaway, learning, or next step
   - Optional invitation for feedback

FORMAT:
- Use line breaks between paragraphs
- Keep sentences clear and readable
- Total length: ~120–180 words

OUTPUT:
Return only the LinkedIn post text.



'''
    response=model.invoke(prompt)
    linkedin_post=response.content
    state["post"]=linkedin_post

    return state

def generating_x_post(state:Gitstate) -> Gitstate:
    prompt=f'''You are a developer and founder sharing progress publicly on X (Twitter).

You are given a concise analytics summary about a GitHub repository’s performance over the last 24 hours.

Your task is to convert this summary into a short, clear, single tweet that:
- Sounds authentic and technical
- Feels like “building in public”
- Is suitable for a normal free-tier X account
- Does NOT rely on threads, images, polls, or advanced features

INPUT:
{state["summary_ans"]}

GUIDELINES:
- Maximum length: 200 characters (stay safely under 280)
- Write in first person (“I” / “we”)
- Plain text only
- No emojis
- No hashtags (or at most 1 at the end)
- No hype or marketing language
- Do not invent numbers or claims
- Focus on insight or learning, not promotion

STYLE:
- Calm
- Direct
- Slightly reflective
- Engineer-to-engineer tone

STRUCTURE:
- One concise sentence or two short sentences
- Optional soft takeaway or observation

OUTPUT:
Return only the tweet text.


'''
    response=model.invoke(prompt)
    x_tweet=response.content
    state["post"]=x_tweet

    return state

def sending_email(state:Gitstate) -> Gitstate:
    msg=MIMEMultipart()
    msg["From"]=SMTP_USER
    msg["To"]="digiance.sagarit@gmail.com"
    msg["Subject"]="Daily Github Summary"
    msg.attach(MIMEText(state["summary_ans"],"plain"))

    server=smtplib.SMTP(SMTP_HOST,SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER,SMTP_PASS)
    server.send_message(msg)
    server.quit()
    state["status"]="sent"

    return state




def router(state:Gitstate) -> str:
    if state["social_type"]=="linkedin":
        return "linkedin"
    elif state["social_type"]=="x":
        return "x"
    else:
        return "error"
    

#building the graph
graph=StateGraph(Gitstate)
graph.add_node("stars",stars_checking)
graph.add_node("traffic",traffic_views)
graph.add_node("summary",llm_summary)
graph.add_node("clones",clones_checking)
graph.add_node("linkedin_post",generating_linkedin_post)
graph.add_node("x_post",generating_x_post)
graph.add_node("sending_mail",sending_email)
graph.add_node("persist_metrics", persist_metrics)



graph.add_edge(START, "stars")
graph.add_edge("stars","traffic")
graph.add_edge("traffic","clones")
graph.add_edge("clones","summary")
graph.add_edge("summary", "persist_metrics")
graph.add_edge("persist_metrics", "sending_mail")
graph.add_conditional_edges(
    "sending_mail",
    router,
    {
        "linkedin":"linkedin_post",
        "x":"x_post",
        "error":END
        
    }

)
graph.add_edge("linkedin_post",END)
graph.add_edge("x_post",END)

app=graph.compile()

previous_metrics = load_previous_metrics()

result = app.invoke(
    {
        "repo_url": "your_repo",
        "social_type":"x/linkedin",
        "previous_metrics": previous_metrics or {
            "stars": 0,
            "views": 0,
            "uni_view": 0,
            "clone": 0,
            "uni_clone": 0
        }
    }
)

result_socialmedia_post=result["post"]
result_mail_status=result["status"]

print(result_socialmedia_post)
print(result_mail_status)