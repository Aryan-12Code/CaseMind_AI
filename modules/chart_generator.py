"""
chart_generator.py — Plotly chart generation for CaseMind AI.

Provides functions to generate dynamic, interactive charts based
on live database metrics and processed evidence data.
"""

import plotly.express as px
import pandas as pd
from collections import Counter
from modules.database import get_all_evidence, get_processed_by_evidence_id


def _get_all_entities_and_keywords() -> tuple[dict, dict]:
    """Helper to aggregate all entities and keywords across all processed files."""
    all_evidence = get_all_evidence()
    
    agg_entities = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "money": []
    }
    
    agg_keywords = {
        "emails": [],
        "phone_numbers": [],
        "dates": [],
        "currency": [],
        "urls": [],
        "numbers": []
    }
    
    for evidence in all_evidence:
        processed = get_processed_by_evidence_id(evidence["id"])
        if processed and processed["processing_status"] == "Completed":
            # Aggregate entities
            entities = processed.get("entities", {})
            for k in agg_entities:
                agg_entities[k].extend(entities.get(k, []))
                
            # Aggregate keywords
            keywords = processed.get("keywords", {})
            for k in agg_keywords:
                agg_keywords[k].extend(keywords.get(k, []))
                
    return agg_entities, agg_keywords


def get_evidence_type_pie_chart():
    """Pie chart showing distribution of uploaded file types."""
    all_evidence = get_all_evidence()
    if not all_evidence:
        return _empty_chart("No Evidence Uploaded")
        
    types = [e["filetype"].upper() for e in all_evidence]
    type_counts = Counter(types)
    
    df = pd.DataFrame(list(type_counts.items()), columns=["Type", "Count"])
    
    fig = px.pie(df, values="Count", names="Type", hole=0.4,
                 color_discrete_sequence=px.colors.sequential.Blues_r,
                 title="Evidence by File Type")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                      font=dict(color="white"), margin=dict(t=40, b=10, l=10, r=10))
    return fig


def get_most_mentioned_people_bar():
    """Bar chart of the top 10 most mentioned people."""
    entities, _ = _get_all_entities_and_keywords()
    persons = entities["persons"]
    
    if not persons:
        return _empty_chart("No People Detected")
        
    counts = Counter(persons).most_common(10)
    df = pd.DataFrame(counts, columns=["Person", "Mentions"])
    
    fig = px.bar(df, x="Person", y="Mentions", color="Person",
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 title="Top 10 Mentioned People")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"), margin=dict(t=40, b=10, l=10, r=10),
                      showlegend=False)
    return fig


def get_keyword_frequency_bar():
    """Horizontal bar chart of keyword frequencies (emails, phones, etc)."""
    _, keywords = _get_all_entities_and_keywords()
    
    # Flatten all keywords except numbers/dates for this chart
    flat_kws = []
    for category in ["emails", "phone_numbers", "currency", "urls"]:
        flat_kws.extend(keywords[category])
        
    if not flat_kws:
        return _empty_chart("No Keywords Detected")
        
    counts = Counter(flat_kws).most_common(10)
    df = pd.DataFrame(counts, columns=["Keyword", "Frequency"])
    
    fig = px.bar(df, x="Frequency", y="Keyword", orientation='h', color="Keyword",
                 color_discrete_sequence=px.colors.sequential.Purp,
                 title="Top 10 Keywords (Emails/Phones/Currency/URLs)")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"), margin=dict(t=40, b=10, l=10, r=10),
                      yaxis={'categoryorder':'total ascending'}, showlegend=False)
    return fig


def get_entity_distribution_pie():
    """Pie chart showing distribution of entity categories."""
    entities, _ = _get_all_entities_and_keywords()
    
    counts = {k.title(): len(v) for k, v in entities.items() if len(v) > 0}
    
    if not counts:
        return _empty_chart("No Entities Detected")
        
    df = pd.DataFrame(list(counts.items()), columns=["Category", "Count"])
    
    fig = px.pie(df, values="Count", names="Category",
                 color_discrete_sequence=px.colors.qualitative.Set3,
                 title="Entity Extraction Distribution")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"), margin=dict(t=40, b=10, l=10, r=10))
    return fig


def get_upload_timeline_line():
    """Line chart showing evidence uploads over time."""
    all_evidence = get_all_evidence()
    if not all_evidence:
        return _empty_chart("No Activity")
        
    # Extract dates (ignore times for grouping)
    dates = [e["upload_time"].split(" ")[0] for e in all_evidence]
    counts = Counter(dates)
    
    df = pd.DataFrame(list(counts.items()), columns=["Date", "Uploads"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    fig = px.line(df, x="Date", y="Uploads", markers=True,
                  title="Evidence Upload Activity",
                  color_discrete_sequence=["#0068c9"])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"), margin=dict(t=40, b=10, l=10, r=10))
    return fig


def _empty_chart(message: str):
    """Helper to return an empty chart with a message."""
    fig = px.scatter(title=message)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"),
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig
