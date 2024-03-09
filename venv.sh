#!/bin/bash
if [ ! -d "venv" ]; then
    echo "Creating virtual env..."
    python -m venv venv
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
else
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
fi