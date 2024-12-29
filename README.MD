# AI Password Generator

This is an AI-powered password generator that can create passwords of any length and complexity based on natural language input. No extra configuration is needed—just describe your desired password, and the generator will handle the rest.

## Features

- **Customizable Length**: Specify the exact length of the password.
- **Character Types**: Include or exclude uppercase letters, lowercase letters, numbers, and special characters.
- **Natural Language Input**: Describe your password requirements in plain language.
- **AI-Driven Configuration**: Uses an AI model to interpret your input and generate the appropriate password configuration.

## Examples

### 6 Character Password with Uppercase Only

**Input**: Enter a password specification: 6 character password with uppercase, not other things

**Output**: Generated password: YQMHSX

### Very Strong Password

**Input**: Enter a password specification: very strong password

**Output**: Generated password: qI=fz",L.5S{D=(t

### 4 Digit PIN

**Input**: Enter a password specification: 4 digit pin

**Output**: Generated password: 3850

## Usage

1. Run the `main.py` script.
2. Enter your password specification when prompted.
3. The generated password will be displayed.

## Requirements

- Python 3.12
- OpenAI (or compitable provider) API key

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install openai
   ```
3. Set your OpenAI API key in the `main.py` script.

## License

This project is licensed under the MIT License.
