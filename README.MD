# PasaiGen - AI Password Generator

An intelligent password generator that creates secure passwords from natural language input, eliminating complex configuration while maintaining security standards.

## Features

- **Natural Language Input**: Convert plain English requirements into secure passwords
- **Smart Configuration**:
   - Customizable length and complexity
   - Character type selection (A-Z, a-z, 0-9, symbols)
   - Pattern-based generation
   - AI-driven security optimization
- **Automatic Validation**: Ensures all requirements and security constraints are met

## Quick Examples

"6 uppercase letters" → YQMHSX
"strong password"    → qI=fz",L.5S{D=(t
"4 digit pin"       → 3850

## Setup

### Requirements
- Python 3.12+
- OpenAI API key (or compatible)

### Installation

git clone https://github.com/mdonmez/PasaiGen.git
cd PasaiGen
pip install -r requirements.txt

# Configure .env file:

BASE_URL=your_api_base_url

API_KEY=your_api_key

MODEL_NAME=your_model_name

### Usage

python main.py
# Follow prompts to generate passwords

## Technical Details

### Components
1. **AI Engine**: Processes natural language, generates configurations
2. **Password Generator**: Implements security rules, validates output

### Security
- Strong randomization
- Balanced character distribution
- Pattern prevention
- Zero password retention
- Configurable complexity

## License

GNU General Public License v3.0 - See [LICENSE](LICENSE)
