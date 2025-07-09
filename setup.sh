#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete!"
echo "You can now run the bot with:"
echo "source venv/bin/activate"
echo "python discord_bot.py"
echo ""
echo "To deactivate the virtual environment later, just type: deactivate"
