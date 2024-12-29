from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import json
import random
import string
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

class PasswordGenerator:
    def __init__(self):
        self.char_sets = {
            'uppercase': string.ascii_uppercase,
            'lowercase': string.ascii_lowercase,
            'numbers': string.digits,
            'special': string.punctuation,
            'ambiguous': 'il1Lo0O',
            'similar': '{}[]()\\\'"`~,;:.<>'
        }

    def get_char_type(self, char: str) -> str:
        if char in self.char_sets['uppercase']: return 'uppercase'
        if char in self.char_sets['lowercase']: return 'lowercase'
        if char in self.char_sets['numbers']: return 'numbers'
        return 'special'

    def validate_requirements(self, length: int, min_counts: Dict[str, int], include: str = '') -> bool:
        effective_length = length - len(include)
        remaining_required = sum(min_counts.values())
        return remaining_required <= effective_length

    def generate_password(
        self,
        length: int = 12,
        use_sets: Dict[str, bool] = None,
        min_counts: Dict[str, int] = None,
        include: str = '',
        exclude: str = '',
        pattern: str = None,
        avoid_ambiguous: bool = False,
        avoid_similar: bool = False,
        consecutive_unique: bool = False
    ) -> str:
        if use_sets is None:
            use_sets = {'uppercase': True, 'lowercase': True, 'numbers': True, 'special': True}
        
        if min_counts is None:
            min_counts = {}

        # Account for included characters in min_counts
        working_min_counts = min_counts.copy()
        for char in include:
            char_type = self.get_char_type(char)
            if char_type in working_min_counts:
                working_min_counts[char_type] = max(0, working_min_counts[char_type] - 1)

        # Validate requirements
        if not self.validate_requirements(length, working_min_counts, include):
            raise ValueError("Password requirements exceed specified length")

        # Build character pool
        chars = ''
        for set_name, use in use_sets.items():
            if use and set_name in self.char_sets:
                chars += self.char_sets[set_name]

        # Apply exclusions
        if avoid_ambiguous:
            exclude += self.char_sets['ambiguous']
        if avoid_similar:
            exclude += self.char_sets['similar']
        chars = ''.join(c for c in chars if c not in exclude)

        if not chars:
            raise ValueError("No valid characters available after applying exclusions")

        # Generate password
        password_chars = list(include)  # Start with required characters
        
        # Add minimum required characters
        for char_set, count in working_min_counts.items():
            valid_chars = [c for c in self.char_sets[char_set] if c in chars]
            if count > 0 and not valid_chars:
                raise ValueError(f"No valid characters available for {char_set}")
            password_chars.extend(random.choices(valid_chars, k=count))

        # Fill remaining length with random characters
        remaining_length = length - len(password_chars)
        if remaining_length > 0:
            password_chars.extend(random.choices(chars, k=remaining_length))

        # Apply pattern if specified
        if pattern:
            pattern_map = {'#': string.digits, '@': string.ascii_letters, '$': string.punctuation}
            final_chars = list(pattern)
            available_chars = password_chars.copy()
            
            for i, pattern_char in enumerate(final_chars):
                if pattern_char in pattern_map:
                    valid_chars = [c for c in available_chars if c in pattern_map[pattern_char]]
                    if not valid_chars:
                        raise ValueError(f"Not enough characters to satisfy pattern at position {i}")
                    chosen_char = random.choice(valid_chars)
                    final_chars[i] = chosen_char
                    available_chars.remove(chosen_char)
            password_chars = final_chars
        else:
            random.shuffle(password_chars)

        # Handle consecutive uniqueness
        if consecutive_unique:
            attempts = 100  # Prevent infinite loop
            while attempts > 0:
                has_consecutive = False
                for i in range(1, len(password_chars)):
                    if password_chars[i] == password_chars[i-1]:
                        has_consecutive = True
                        break
                if not has_consecutive:
                    break
                random.shuffle(password_chars)
                attempts -= 1
            if attempts == 0:
                raise ValueError("Could not generate password with unique consecutive characters")

        return ''.join(password_chars)

def get_password_config(user_input: str) -> Dict[str, Any]:
    system_prompt = """You are a password configuration analyzer. Convert user requests into a precise JSON configuration. Return ONLY a JSON object.

Required JSON format:
{
    "length": <integer>,  // Default: 12, Range: 4-128
    "use_sets": {
        "uppercase": <boolean>,  // Enable A-Z
        "lowercase": <boolean>,  // Enable a-z
        "numbers": <boolean>,    // Enable 0-9
        "special": <boolean>     // Enable !@#$%^&*()
    },
    "min_counts": {
        "uppercase": <integer>,  // Minimum required uppercase
        "lowercase": <integer>,  // Minimum required lowercase
        "numbers": <integer>,    // Minimum required numbers
        "special": <integer>     // Minimum required special
    },
    "include": "<specific characters to include>",  // Exact characters to include
    "exclude": "<characters to exclude>",           // Exact characters to exclude
    "pattern": "<pattern string>",                  // Use #@$ for number/letter/special
    "avoid_ambiguous": <boolean>,                  // Avoid il1Lo0O
    "avoid_similar": <boolean>,                    // Avoid {}[]()\'"`~,;:.<>
    "consecutive_unique": <boolean>                // No repeated adjacent chars
}

Examples:
1. "Generate secure 16 character password with at least 2 numbers":
{
    "length": 16,
    "use_sets": {"uppercase": true, "lowercase": true, "numbers": true, "special": true},
    "min_counts": {"numbers": 2},
    "include": "",
    "exclude": "",
    "pattern": null,
    "avoid_ambiguous": false,
    "avoid_similar": false,
    "consecutive_unique": false
}

2. "Create a PIN with 6 digits":
{
    "length": 6,
    "use_sets": {"uppercase": false, "lowercase": false, "numbers": true, "special": false},
    "min_counts": {"numbers": 6},
    "include": "",
    "exclude": "",
    "pattern": null,
    "avoid_ambiguous": false,
    "avoid_similar": false,
    "consecutive_unique": false
}

Key Rules:
1. Always validate length against min_counts + include field
2. Enable only necessary character sets based on request
3. Set appropriate min_counts based on user requirements
4. Pattern uses: # (number), @ (letter), $ (special)
5. Default to secure settings when request is ambiguous
6. Consider common password policy requirements
7. Handle numeric-only requests appropriately
8. Process natural language indicators like 'avoid similar characters'"""


    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    try:
        config = json.loads(response.choices[0].message.content)
        return config
    except json.JSONDecodeError:
        raise ValueError("Failed to parse AI response as JSON")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        user_input = request.form.get('specification', '')
        config = get_password_config(user_input)
        
        generator = PasswordGenerator()
        password = generator.generate_password(
            length=config.get("length", 12),
            use_sets=config.get("use_sets", None),
            min_counts=config.get("min_counts", None),
            include=config.get("include", ""),
            exclude=config.get("exclude", ""),
            pattern=config.get("pattern", None),
            avoid_ambiguous=config.get("avoid_ambiguous", False),
            avoid_similar=config.get("avoid_similar", False),
            consecutive_unique=config.get("consecutive_unique", False)
        )
        
        return jsonify({'password': password, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

if __name__ == '__main__':
    app.run(debug=True)
