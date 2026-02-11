#!/usr/bin/env python3
"""Main CLI application for the AI Research Assistant."""

import sys
import json
from pathlib import Path

import click

from config import load_config, PROJECT_ROOT
from indexer import DocumentIndexer
from qa_agent import ResearchAssistantAgent
from utils import logger, setup_logging


@click.group()
@click.option("--config", default=None, help="Path to config file")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, config, debug):
    """AI Research Assistant - Semantic search and QA with Endee vector database."""
    # Load configuration
    app_config = load_config()
    
    if debug:
        app_config.debug = True
        app_config.log_level = "DEBUG"
    
    # Setup logging
    setup_logging(app_config)
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = app_config


@cli.command()
@click.option("--source", default="data", help="Source directory for documents")
@click.option("--clear", is_flag=True, help="Clear existing index before indexing")
@click.pass_context
def index(ctx, source, clear):
    """Index documents from a directory."""
    config = ctx.obj['config']
    indexer = DocumentIndexer(config)
    
    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = PROJECT_ROOT / source
    
    if clear:
        click.echo("Clearing existing index...")
        indexer.clear_index()
    
    click.echo(f"Indexing documents from: {source_path}")
    count = indexer.index_directory(source_path)
    
    if count > 0:
        click.echo(f"✓ Successfully indexed {count} document chunks")
    else:
        click.echo("⚠ No documents indexed")


@cli.command()
@click.argument("question")
@click.option("--top-k", default=5, help="Number of results to retrieve")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def query(ctx, question, top_k, output_json):
    """Query the knowledge base."""
    config = ctx.obj['config']
    agent = ResearchAssistantAgent(config)
    
    result = agent.answer_question(question, top_k=top_k)
    
    if output_json:
        output = {
            "question": result.question,
            "answer": result.answer,
            "confidence": result.confidence,
            "sources": result.sources,
            "retrieved_docs_count": result.retrieved_docs_count,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo("\n" + "="*80)
        click.echo(f"Q: {result.question}")
        click.echo("="*80)
        click.echo(f"\nA: {result.answer}\n")
        click.echo(f"Confidence: {result.confidence:.2%}")
        click.echo(f"Retrieved documents: {result.retrieved_docs_count}")
        
        if result.sources:
            click.echo("\nSources:")
            for source in result.sources:
                click.echo(
                    f"  • {source['source']} (chunk {source['chunk_id']}, "
                    f"similarity: {source['similarity']})"
                )


@cli.command()
@click.pass_context
def chat(ctx):
    """Start interactive chat session."""
    config = ctx.obj['config']
    agent = ResearchAssistantAgent(config)
    agent.interactive_chat()


@cli.command()
@click.option("--queries", multiple=True, help="Query strings")
@click.option("--file", type=click.File('r'), help="File with queries (one per line)")
@click.option("--output", type=click.File('w'), default="-", help="Output file")
@click.pass_context
def batch(ctx, queries, file, output):
    """Process multiple queries in batch mode."""
    config = ctx.obj['config']
    agent = ResearchAssistantAgent(config)
    
    # Collect queries
    all_queries = list(queries)
    
    if file:
        all_queries.extend(line.strip() for line in file if line.strip())
    
    if not all_queries:
        click.echo("No queries provided")
        return
    
    click.echo(f"Processing {len(all_queries)} queries...\n")
    
    results = agent.batch_answer(all_queries)
    
    # Output results
    output_data = []
    for result in results:
        output_data.append({
            "question": result.question,
            "answer": result.answer,
            "confidence": result.confidence,
            "sources": result.sources,
            "retrieved_docs_count": result.retrieved_docs_count,
        })
    
    output.write(json.dumps(output_data, indent=2))
    click.echo(f"✓ Results written to output")


@cli.command()
@click.pass_context
def info(ctx):
    """Display system information."""
    config = ctx.obj['config']
    
    click.echo("\n" + "="*80)
    click.echo("AI Research Assistant - System Information")
    click.echo("="*80 + "\n")
    
    click.echo("Endee Configuration:")
    click.echo(f"  Base URL: {config.endee.base_url}")
    click.echo(f"  Index Name: {config.endee.index_name}")
    click.echo(f"  Vector Dimension: {config.endee.vector_dim}")
    click.echo(f"  Space Type: {config.endee.space_type}\n")
    
    click.echo("Embedding Configuration:")
    click.echo(f"  Model: {config.embedding.model_name}")
    click.echo(f"  Device: {config.embedding.device}")
    click.echo(f"  Batch Size: {config.embedding.batch_size}\n")
    
    click.echo("LLM Configuration:")
    click.echo(f"  Provider: {config.llm.provider}")
    click.echo(f"  Model: {config.llm.model_name}")
    click.echo(f"  Temperature: {config.llm.temperature}\n")
    
    click.echo("Retrieval Settings:")
    click.echo(f"  Top K: {config.top_k}")
    click.echo(f"  Similarity Threshold: {config.similarity_threshold}\n")
    
    click.echo("Data Paths:")
    click.echo(f"  Project Root: {PROJECT_ROOT}")
    click.echo(f"  Data Directory: {PROJECT_ROOT / 'data'}")
    click.echo(f"  Logs Directory: {PROJECT_ROOT / 'logs'}\n")


@cli.command()
@click.pass_context
def clear(ctx):
    """Clear the index."""
    if not click.confirm("Are you sure you want to clear the index? This cannot be undone."):
        click.echo("Aborted")
        return
    
    config = ctx.obj['config']
    indexer = DocumentIndexer(config)
    
    if indexer.clear_index():
        click.echo("✓ Index cleared successfully")
    else:
        click.echo("✗ Failed to clear index")


if __name__ == "__main__":
    cli(obj={})
