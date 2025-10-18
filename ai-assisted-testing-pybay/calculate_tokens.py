#!/usr/bin/env python3
"""
Calculate total tokens used and duration from Claude 45 logs JSON file.

This script reads the claude45_logs.json file and extracts all usage.total_tokens 
values and duration information to calculate the total resources consumed across all requests.

Usage:
    python calculate_tokens.py [path_to_logs.json]
    
If no path is provided, it defaults to claude45_logs.json in the same directory.
"""

import json
import sys
from pathlib import Path


def extract_usage_data(data, usage_data_list=None):
    """
    Recursively extract all usage data including tokens, duration, and timestamps from nested JSON structure.
    
    Args:
        data: JSON data (dict, list, or primitive)
        usage_data_list: List to accumulate usage data
    
    Returns:
        List of dictionaries with usage information found
    """
    if usage_data_list is None:
        usage_data_list = []
    
    if isinstance(data, dict):
        # Check if this dict has usage.total_tokens and/or duration/time info
        usage_info = {}
        
        if "usage" in data and isinstance(data["usage"], dict):
            if "total_tokens" in data["usage"]:
                usage_info["total_tokens"] = data["usage"]["total_tokens"]
        
        if "duration" in data:
            usage_info["duration_ms"] = data["duration"]
        
        if "startTime" in data:
            usage_info["start_time"] = data["startTime"]
        
        if "endTime" in data:
            usage_info["end_time"] = data["endTime"]
        
        if "time" in data:
            usage_info["time"] = data["time"]
        
        # Only add if we found some usage data
        if usage_info:
            usage_data_list.append(usage_info)
        
        # Recursively search all values in the dict
        for value in data.values():
            extract_usage_data(value, usage_data_list)
    
    elif isinstance(data, list):
        # Recursively search all items in the list
        for item in data:
            extract_usage_data(item, usage_data_list)
    
    return usage_data_list


def format_duration(milliseconds):
    """Format duration in milliseconds to human-readable format."""
    if milliseconds < 1000:
        return f"{milliseconds}ms"
    elif milliseconds < 60000:
        return f"{milliseconds/1000:.1f}s"
    elif milliseconds < 3600000:
        minutes = milliseconds // 60000
        seconds = (milliseconds % 60000) / 1000
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = milliseconds // 3600000
        minutes = (milliseconds % 3600000) // 60000
        seconds = ((milliseconds % 3600000) % 60000) / 1000
        return f"{hours}h {minutes}m {seconds:.1f}s"


def parse_iso_timestamp(timestamp_str):
    """Parse ISO timestamp string to datetime object."""
    from datetime import datetime
    # Remove 'Z' and parse
    if timestamp_str.endswith('Z'):
        timestamp_str = timestamp_str[:-1] + '+00:00'
    return datetime.fromisoformat(timestamp_str)


def calculate_session_duration(usage_data):
    """Calculate total session duration from start to end timestamps."""
    timestamps = []
    
    for entry in usage_data:
        if "start_time" in entry:
            timestamps.append(parse_iso_timestamp(entry["start_time"]))
        if "end_time" in entry:
            timestamps.append(parse_iso_timestamp(entry["end_time"]))
        if "time" in entry:
            timestamps.append(parse_iso_timestamp(entry["time"]))
    
    if not timestamps:
        return None
    
    earliest = min(timestamps)
    latest = max(timestamps)
    duration_seconds = (latest - earliest).total_seconds()
    return duration_seconds * 1000  # Convert to milliseconds


def main():
    """Main function to process the Claude 45 logs and calculate total tokens and duration."""
    
    # Default file path
    log_file = Path(__file__).parent / "claude45_logs.json"
    
    # Allow specifying a different file path as command line argument
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    
    if not log_file.exists():
        print(f"Error: File {log_file} not found")
        sys.exit(1)
    
    print(f"Processing {log_file}...")
    
    try:
        # Load the JSON data
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract all usage data
        usage_data = extract_usage_data(data)
        
        # Filter entries with tokens
        token_entries = [entry for entry in usage_data if "total_tokens" in entry]
        
        # Filter entries with duration
        duration_entries = [entry for entry in usage_data if "duration_ms" in entry]
        
        if not token_entries:
            print("No usage.total_tokens values found in the file")
            return
        
        # Calculate token statistics
        token_counts = [entry["total_tokens"] for entry in token_entries]
        total_tokens = sum(token_counts)
        num_requests = len(token_counts)
        avg_tokens = total_tokens / num_requests if num_requests > 0 else 0
        
        # Calculate duration statistics
        if duration_entries:
            durations = [entry["duration_ms"] for entry in duration_entries]
            total_duration = sum(durations)
            avg_duration = total_duration / len(durations) if durations else 0
        else:
            durations = []
            total_duration = 0
            avg_duration = 0
        
        # Calculate session duration
        session_duration = calculate_session_duration(usage_data)
        
        # Display results
        print("\n" + "="*60)
        print("TOKEN AND DURATION USAGE SUMMARY")
        print("="*60)
        
        # Token statistics
        print(f"Total number of requests with tokens: {num_requests:,}")
        print(f"Total tokens used: {total_tokens:,}")
        print(f"Average tokens per request: {avg_tokens:,.1f}")
        print(f"Minimum tokens in a request: {min(token_counts):,}")
        print(f"Maximum tokens in a request: {max(token_counts):,}")
        
        # Duration statistics
        if durations:
            print(f"\nTotal number of requests with duration: {len(durations):,}")
            print(f"Total processing time: {format_duration(total_duration)}")
            print(f"Average processing time per request: {format_duration(avg_duration)}")
            print(f"Minimum processing time: {format_duration(min(durations))}")
            print(f"Maximum processing time: {format_duration(max(durations))}")
        
        # Session duration
        if session_duration:
            print(f"\nOverall session duration: {format_duration(session_duration)}")
        
        # Show breakdown by request
        print("\nPer-request breakdown:")
        for i, entry in enumerate(token_entries, 1):
            tokens = entry["total_tokens"]
            duration_info = ""
            
            # Find matching duration entry (they might not be 1:1 mapped)
            if i <= len(durations):
                duration_ms = durations[i-1]
                duration_info = f" ({format_duration(duration_ms)})"
            
            print(f"Request {i:2d}: {tokens:,} tokens{duration_info}")
        
        print(f"\nGrand total: {total_tokens:,} tokens")
        if total_duration > 0:
            print(f"Total processing time: {format_duration(total_duration)}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()