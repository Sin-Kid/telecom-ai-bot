#!/bin/bash

echo "🚀 Setting up Telecom AI Bot Project..."
echo ""

# Create project directories
echo "📁 Creating project structure..."
mkdir -p telecom-ai-bot
cd telecom-ai-bot

mkdir -p backend/data
mkdir -p backend/actions
mkdir -p frontend
mkdir -p data
mkdir -p models
mkdir -p notebooks
mkdir -p config

echo "✓ Directories created"
echo ""

# Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Core
python-dotenv==1.0.0
requests==2.31.0

# Backend API
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# NLU & ML
rasa==3.5.0
rasa-sdk==3.5.0

# ML Utils
scikit-learn==1.3.2
numpy==1.24.3
pandas==1.5.3

# Data
pyyaml==6.0

# Utils
typing-extensions==4.8.0
EOF

echo "✓ requirements.txt created"
echo ""

# Create .env template
echo "🔐 Creating .env template..."
cat > .env << 'EOF'
# Sarvam AI Credentials (Get from https://www.sarvam.ai/)
SARVAM_API_KEY=your_api_key_here

# App Settings
ENVIRONMENT=development
DEBUG=True

# Supported Languages
LANGUAGES=hi,ta,te,en,kn

# Database
DATABASE_PATH=./data/telecom_bot.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5000
EOF

echo "✓ .env template created"
echo ""

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "On Windows, activate with: venv\Scripts\activate"
    source venv/Scripts/activate
else
    echo "On Mac/Linux, activate with: source venv/bin/activate"
    source venv/bin/activate
fi

echo "✓ Virtual environment created"
echo ""

# Install dependencies
echo "📥 Installing dependencies (this may take 5-10 minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Create .gitignore
echo "🙈 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Virtual environment
venv/
ENV/
env/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/

# Database
*.db
*.sqlite
data/

# Rasa
.rasa/
models/

# Logs
*.log
logs/
EOF

echo "✓ .gitignore created"
echo ""

echo "============================================"
echo "✅ Project setup complete!"
echo "============================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Edit .env and add your SARVAM_API_KEY"
echo "   Get it from: https://www.sarvam.ai/"
echo ""
echo "2. Activate virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\Scripts\activate"
else
    echo "   source venv/bin/activate"
fi
echo ""
echo "3. Verify installation:"
echo "   python --version"
echo "   pip list"
echo ""
echo "4. Start building Phase 1!"
echo ""
