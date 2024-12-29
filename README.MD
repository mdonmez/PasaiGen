# PasaiGen - AI Password Generator

A sophisticated AI-powered password generator that creates secure passwords based on natural language input. This tool intelligently interprets user requirements to generate passwords that meet specific criteria without complex configuration.

## Overview

The AI Password Generator leverages natural language processing to create passwords that match user-specified requirements for length, complexity, and character composition. It provides a seamless interface between human-readable password requirements and secure password generation.

## Key Features

- **Natural Language Processing**: Interpret password requirements from plain English descriptions
- **Flexible Configuration**:
  - Custom password length
  - Selective character type inclusion (uppercase, lowercase, numbers, special characters)
  - Pattern-based generation
  - Configurable complexity levels
- **Smart Generation**: AI-driven configuration ensures password security while meeting specified requirements
- **Validation**: Automatic verification of password requirements and constraints

## Usage Examples

### Basic Examples

1. **Simple Uppercase Password**
   
   Input: "6 character password with uppercase only"
   Output: YQMHSX
   

2. **High Security Password**
   
   Input: "very strong password"
   Output: qI=fz",L.5S{D=(t
   

3. **Numeric PIN**
   
   Input: "4 digit pin"
   Output: 3850
   

## Getting Started

### Prerequisites

- Python 3.12 or higher
- OpenAI API key (or an API key from a compatible provider)

### Installation

1. Clone the repository:
   
   git clone https://github.com/mdonmez/PasaiGen.git
   cd PasaiGen
   

2. Install dependencies:
   
   pip install -r requirements.txt
   

3. Configure environment variables:
   Create a `.env` file with the following:
   
   BASE_URL=your_api_base_url
   API_KEY=your_api_key
   MODEL_NAME=your_model_name
   

### Quick Start

1. Run the application:
   
   python main.py
   
2. Enter your password requirements when prompted
3. Receive your generated password

## Technical Implementation

### Architecture Overview

The system consists of two main components:

1. **AI Configuration Engine**
   - Processes natural language input
   - Generates structured password configuration
   - Handles requirement interpretation

2. **Password Generation Engine**
   - Implements security constraints
   - Manages character set composition
   - Ensures requirement compliance

### Generation Process

1. **Input Processing**
   - Natural language parsing
   - Requirement extraction
   - Configuration generation

2. **Password Assembly**
   - Character pool creation
   - Requirement validation
   - Pattern matching
   - Uniqueness verification

3. **Output Validation**
   - Security check
   - Requirement compliance verification
   - Pattern confirmation

## Security Considerations

- Implements strong randomization
- Ensures character distribution
- Prevents predictable patterns
- Maintains specified complexity requirements
- AI can't see generated passwords

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
