
# GitHub Tracker Agent 🚀

**Built in under 24 hours | Founder + Builder Energy**

---

## What is this?

GitHub Tracker Agent is your **personal GitHub growth analyst**. It tracks key repository metrics every 24 hours (or on demand), compares them to the previous period, and gives you **actionable insights**.  

- Stars ⭐  
- Traffic Views 👀  
- Unique Visitors  
- Clones 📥  
- Unique Cloners  

It doesn’t just give raw numbers—it generates **professional summaries**, ready-to-post **LinkedIn updates**, **X (Twitter) posts**, and even **daily email reports**.

---

## Features

- **Automated Metric Tracking** – fetch stars, views, clones from any repo.  
- **Historical Comparison** – keeps track of previous metrics to analyze trends.  
- **AI-Generated Summaries** – clear, analytical breakdown of your repository growth.  
- **Social Media Ready** – LinkedIn & X post templates automatically generated.  
- **Email Reports** – daily summary sent straight to your inbox.  

---

## Tech Stack

- Python 3.13  
- [LangGraph + ChatGroq](https://www.groq.com/) for LLM summaries  
- GitHub REST API v3 for metrics  
- SMTP for email notifications  
- JSON for storing historical metrics  

---

## How to Run

1. Clone this repo:
```bash
git clone https://github.com/yourusername/github-agent.git
cd github-agent
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your `.env` file with:

```
GITHUB_TOKEN=your_github_token
GROQ_API_KEY=your_llm_api_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASS=your_email_password
```

4. Run the agent:

```bash
python agent.py
```

5. Outputs:

* Console: social media-ready posts
* `metrics_history.json`: stored metrics for next comparison
* Emails sent (if configured)

---

## How it Works

1. Fetch **current metrics** from GitHub.
2. Compare with **previous metrics** saved in `metrics_history.json`.
3. Generate **AI-powered analysis** using ChatGroq.
4. Output **LinkedIn/X post** or send **email report**.
5. Update `metrics_history.json` with the latest data.

---

## Example Output

**X Post:**

```
We've seen a notable increase in clones and traffic to Example Repository over the last 24 hours, but star growth has been moderate. Time to review and optimize the README and engage with the community to better understand and leverage this interest.
```

**LinkedIn Post:**

```
As the founder of Example Repository, I've been observing its performance over the past 24 hours. The repository has experienced a relatively flat period, with some slight increases and decreases in key metrics...

#RepositoryPerformance #CommunityEngagement
```

---

## License

MIT License – feel free to use, fork, and build on it.

---

**Built fast. Built smart. Built in public.**

```

---

If you want, I can **also make a visually sexy GIF/diagram version of this README**, showing the workflow from GitHub → Metrics → AI → LinkedIn/X → Email. That would make it super pro for showing off.  

Do you want me to do that next?
```
