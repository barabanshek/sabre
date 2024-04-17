#!/bin/bash

find . -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
    echo "Building Docker image in directory: $dir"
    
    # Extract the directory name to use as the tag
    dir_name=$(basename "$dir")

    # Change to the directory
    cd "$dir" || { echo "Failed to enter directory $dir"; continue; }

    # Run Docker build with the directory name as the tag
    docker build -t localhost:5000/"$dir_name" .
    docker push localhost:5000/"$dir_name"

    # Optionally, return to the parent directory
    cd - > /dev/null
done
