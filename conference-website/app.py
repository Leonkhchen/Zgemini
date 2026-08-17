import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Mock database of speakers
SPEAKERS = {
    "sarah_chen": {
        "first_name": "Sarah",
        "last_name": "Chen",
        "title": "Lead AI Advocate",
        "company": "Google Cloud",
        "bio": "Sarah Chen is a Lead AI Advocate at Google Cloud, specializing in large language models and cognitive agent architectures. She helps enterprises build production-grade GenAI workflows.",
        "linkedin": "https://www.linkedin.com/in/sarahchen-gcp"
    },
    "alex_rodriguez": {
        "first_name": "Alex",
        "last_name": "Rodriguez",
        "title": "Principal Developer Advocate",
        "company": "Google Cloud",
        "bio": "Alex focuses on Vertex AI platform tools and developer experience. He is a frequent contributor to open-source ML tooling.",
        "linkedin": "https://www.linkedin.com/in/alexrodriguez-gcp"
    },
    "marcus_vance": {
        "first_name": "Marcus",
        "last_name": "Vance",
        "title": "Senior Solutions Architect",
        "company": "Google Cloud",
        "bio": "Marcus is a GKE specialist with over a decade of experience in Kubernetes, container networking, and microservice architectures at scale.",
        "linkedin": "https://www.linkedin.com/in/marcusvance-gke"
    },
    "priya_sharma": {
        "first_name": "Priya",
        "last_name": "Sharma",
        "title": "Director of Data Engineering",
        "company": "Google Cloud",
        "bio": "Priya leads the BigQuery developer relations team. She is passionate about serverless data warehousing and hybrid-cloud analytics.",
        "linkedin": "https://www.linkedin.com/in/priyasharma-bigquery"
    },
    "john_doe": {
        "first_name": "John",
        "last_name": "Doe",
        "title": "Data Architect",
        "company": "Google Cloud",
        "bio": "John helps clients build robust and secure analytics architectures on GCP, focusing on cross-cloud query capabilities.",
        "linkedin": "https://www.linkedin.com/in/johndoe-data"
    },
    "elena_rostova": {
        "first_name": "Elena",
        "last_name": "Rostova",
        "title": "Security Specialist",
        "company": "Google Cloud",
        "bio": "Elena has designed security architectures for global financial institutions and is an expert in BeyondCorp Enterprise and Zero Trust.",
        "linkedin": "https://www.linkedin.com/in/elenarostova-security"
    },
    "david_kim": {
        "first_name": "David",
        "last_name": "Kim",
        "title": "Database Engineer",
        "company": "Google Cloud",
        "bio": "David is on the Cloud Spanner product engineering team, focusing on globally-distributed consensus models and database engine tuning.",
        "linkedin": "https://www.linkedin.com/in/davidkim-spanner"
    },
    "emily_watson": {
        "first_name": "Emily",
        "last_name": "Watson",
        "title": "Serverless Developer Advocate",
        "company": "Google Cloud",
        "bio": "Emily is a web engineer turned cloud specialist who loves building lightweight, event-driven microservices using Cloud Run and Eventarc.",
        "linkedin": "https://www.linkedin.com/in/emilywatson-cloudrun"
    },
    "raj_patel": {
        "first_name": "Raj",
        "last_name": "Patel",
        "title": "Solutions Architect",
        "company": "Google Cloud",
        "bio": "Raj helps startups scale modern applications on serverless GCP runtimes, automating infrastructure with Terraform.",
        "linkedin": "https://www.linkedin.com/in/rajpatel-serverless"
    },
    "carlos_mendez": {
        "first_name": "Carlos",
        "last_name": "Mendez",
        "title": "Streaming Analytics Specialist",
        "company": "Google Cloud",
        "bio": "Carlos helps design real-time IoT and telemetry streaming platforms. He is a regular contributor to the Apache Beam project.",
        "linkedin": "https://www.linkedin.com/in/carlosmendez-dataflow"
    },
    "aisha_almansoor": {
        "first_name": "Aisha",
        "last_name": "Al-Mansoor",
        "title": "Staff Research Scientist",
        "company": "Google Cloud AI",
        "bio": "Aisha leads efforts in domain alignment and model fine-tuning for Google's Gemini models, with a focus on safety and compliance.",
        "linkedin": "https://www.linkedin.com/in/aishaalmansoor-gemini"
    }
}

# Mock database of talks
# Category 1: AI & Modern Data Analytics
# Category 2: Cloud Infrastructure, DevOps & Security
TALKS = [
    {
        "id": "T1",
        "time": "09:00 - 09:40",
        "title": "Building Generative AI Applications with Vertex AI and Gemini",
        "category": "AI & Modern Data Analytics",
        "category_id": 1,
        "description": "Learn how to leverage Google Cloud's Vertex AI platform and Gemini models to build, tune, and deploy enterprise-grade generative AI applications. This session covers prompt engineering, vector search, and agentic workflows.",
        "speakers": ["sarah_chen", "alex_rodriguez"]
    },
    {
        "id": "T2",
        "time": "09:45 - 10:25",
        "title": "Architecting Resilient Services on Google Kubernetes Engine (GKE)",
        "category": "Cloud Infrastructure, DevOps & Security",
        "category_id": 2,
        "description": "Deep dive into advanced GKE patterns including multi-cluster routing, service mesh configurations, and auto-scaling practices to ensure maximum availability and fault tolerance for enterprise microservices.",
        "speakers": ["marcus_vance"]
    },
    {
        "id": "B1",
        "time": "10:25 - 10:45",
        "title": "Morning Coffee & Networking Break",
        "category": "Break",
        "category_id": 0,
        "description": "Re-energize with custom-blend coffee and connect with fellow tech enthusiasts at our networking hubs.",
        "speakers": []
    },
    {
        "id": "T3",
        "time": "10:45 - 11:25",
        "title": "Next-Generation Data Warehousing with BigQuery Omni",
        "category": "AI & Modern Data Analytics",
        "category_id": 1,
        "description": "Discover how to analyze data across multi-cloud environments (AWS, Azure, GCP) seamlessly using BigQuery Omni. We will explore cross-cloud queries, performance tuning, and cost-optimization strategies.",
        "speakers": ["priya_sharma", "john_doe"]
    },
    {
        "id": "T4",
        "time": "11:30 - 12:10",
        "title": "Securing the Cloud: Zero Trust Architecture in Google Cloud",
        "category": "Cloud Infrastructure, DevOps & Security",
        "category_id": 2,
        "description": "Understand the fundamentals of Google Cloud's BeyondCorp Enterprise and Zero Trust methodologies. Learn to implement context-aware access policies, secure APIs, and protect sensitive data at scale.",
        "speakers": ["elena_rostova"]
    },
    {
        "id": "LUNCH",
        "time": "12:10 - 13:10",
        "title": "Lunch Break & Partner Demos",
        "category": "Break",
        "category_id": 0,
        "description": "Enjoy a curated gourmet lunch and visit Google Cloud partner booths in the main exhibition hall for live product demos.",
        "speakers": []
    },
    {
        "id": "T5",
        "time": "13:15 - 13:55",
        "title": "Scaling Globally with Google Cloud Spanner",
        "category": "Cloud Infrastructure, DevOps & Security",
        "category_id": 2,
        "description": "Learn how Cloud Spanner provides relational semantics with unlimited horizontal scale and 99.999% availability. This session covers database schema design, global transactions, and performance monitoring.",
        "speakers": ["david_kim"]
    },
    {
        "id": "T6",
        "time": "14:00 - 14:40",
        "title": "Modern Application Deployment with Cloud Run and Eventarc",
        "category": "Cloud Infrastructure, DevOps & Security",
        "category_id": 2,
        "description": "Explore how serverless architectures are shifting. Build event-driven web applications using Cloud Run, Cloud Workflows, and Eventarc to react to changes from cloud resources in real time.",
        "speakers": ["emily_watson", "raj_patel"]
    },
    {
        "id": "B2",
        "time": "14:40 - 15:00",
        "title": "Afternoon Refreshments Break",
        "category": "Break",
        "category_id": 0,
        "description": "Unwind with cold drinks and snacks before the final technical sessions.",
        "speakers": []
    },
    {
        "id": "T7",
        "time": "15:00 - 15:40",
        "title": "Unlocking Value from Streaming Data with Cloud Dataflow",
        "category": "AI & Modern Data Analytics",
        "category_id": 1,
        "description": "Real-time analytics is critical for modern business. Learn how to construct streaming data pipelines using Apache Beam and Cloud Dataflow to ingest, process, and analyze massive message volumes in real-time.",
        "speakers": ["carlos_mendez"]
    },
    {
        "id": "T8",
        "time": "15:45 - 16:25",
        "title": "Fine-Tuning Gemini Models for Domain-Specific Tasks",
        "category": "AI & Modern Data Analytics",
        "category_id": 1,
        "description": "Go beyond basic prompting. In this technical walkthrough, learn how to fine-tune Gemini models using custom datasets, evaluate alignment and safety metrics, and deploy the tuned models on Vertex AI.",
        "speakers": ["aisha_almansoor"]
    }
]

CONFERENCE_INFO = {
    "name": "GCP NextGen Summit 2026",
    "date": "October 15, 2026",
    "location": "Google Partner Innovation Dome, San Francisco, CA & Virtual",
    "description": "A premier 1-day technical conference dedicated to exploring Google Cloud's leading edge in Generative AI, global databases, serverless computing, security architectures, and advanced analytics."
}

def get_rich_talks():
    """Helper to join speakers details with talks."""
    rich_talks = []
    for talk in TALKS:
        talk_copy = talk.copy()
        talk_copy["speakers"] = [SPEAKERS[s_id] for s_id in talk["speakers"]]
        rich_talks.append(talk_copy)
    return rich_talks

@app.route("/")
def home():
    return render_template("index.html", conference=CONFERENCE_INFO, talks=get_rich_talks())

@app.route("/api/schedule")
def get_schedule():
    return jsonify({
        "conference": CONFERENCE_INFO,
        "talks": get_rich_talks(),
        "speakers": SPEAKERS
    })

if __name__ == "__main__":
    # Standard Flask run
    app.run(host="0.0.0.0", port=5000, debug=True)
