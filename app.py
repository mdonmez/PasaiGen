from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import json
import random
import string
import secrets
from typing import Dict, Any, List, Optional, Union
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

@dataclass
class PasswordConfig:
    length: int
    complexity: str = "medium"
    type: str = "password"
    memorability: str = "standard"
    use_sets: Dict[str, bool] = field(default_factory=lambda: {
        'uppercase': True,
        'lowercase': True,
        'numbers': True,
        'special': True
    })
    min_counts: Dict[str, int] = field(default_factory=dict)
    include: str = ""
    exclude: str = ""
    pattern: Optional[str] = None
    avoid_ambiguous: bool = False
    avoid_similar: bool = False
    consecutive_unique: bool = False
    word_separator: str = "-"
    capitalize_words: bool = False
    num_words: int = 4
    word_length: Optional[int] = None
    leetspeak: bool = False
    semantic_group: Optional[str] = None

class EnhancedPasswordGenerator:
    def __init__(self):
        self.char_sets = {
            'uppercase': string.ascii_uppercase,
            'lowercase': string.ascii_lowercase,
            'numbers': string.digits,
            'special': "!@#$%^&*()_+-=[]{}|;:,.<>?",
            'ambiguous': 'il1Lo0O',
            'similar': '{}[]()\\\'"`~,;:.<>',
            'hex': string.hexdigits,
            'base32': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
        }
        
        self.complexity_presets = {
            'low': {
                'use_sets': {'uppercase': False, 'lowercase': True, 'numbers': True, 'special': False},
                'min_counts': {'lowercase': 1, 'numbers': 1},
                'length': 8
            },
            'medium': {
                'use_sets': {'uppercase': True, 'lowercase': True, 'numbers': True, 'special': True},
                'min_counts': {'uppercase': 1, 'lowercase': 1, 'numbers': 1, 'special': 1},
                'length': 12
            },
            'high': {
                'use_sets': {'uppercase': True, 'lowercase': True, 'numbers': True, 'special': True},
                'min_counts': {'uppercase': 2, 'lowercase': 2, 'numbers': 2, 'special': 2},
                'length': 16,
                'consecutive_unique': True,
                'avoid_ambiguous': True
            }
        }

        self.memorability_presets = {
            'easy': {
                'word_length_max': 6,
                'use_leetspeak': True,
                'word_separator': '-',
                'capitalize_words': True
            },
            'standard': {
                'word_length_max': 8,
                'use_leetspeak': False,
                'word_separator': '',
                'capitalize_words': False
            },
            'complex': {
                'avoid_similar': True,
                'consecutive_unique': True,
                'pattern': None
            }
        }

        self.leetspeak_map = {
            'a': '@', 'e': '3', 'i': '1',
            'o': '0', 's': '$', 't': '7'
        }

        self.semantic_words = {
            'colors': ['red', 'blue', 'green', 'gold', 'silver', 'black', 'white', 'purple'],
            'animals': ['wolf', 'bear', 'eagle', 'tiger', 'lion', 'deer', 'hawk', 'fox'],
            'foods': ['pizza', 'pasta', 'sushi', 'taco', 'cake', 'bread', 'apple', 'rice']
        }
        
        self.word_list = self._load_word_list()

    def _load_word_list(self) -> List[str]:
        base_words = ['correct', 'horse', 'battery', 'staple', 'apple', 'banana', 'orange', 'grape']
        return base_words + [word for words in self.semantic_words.values() for word in words]

    def _get_char_type(self, char: str) -> str:
        for set_name, char_set in self.char_sets.items():
            if char in char_set:
                return set_name
        return 'special'

    def _validate_config(self, config: PasswordConfig) -> bool:
        if config.type == "passphrase":
            return len(self.word_list) >= config.num_words
            
        effective_length = config.length - len(config.include)
        if config.min_counts:
            required_chars = sum(config.min_counts.values())
            if required_chars > effective_length:
                raise ValueError("Minimum character requirements exceed password length")
        return True

    def _generate_passcode(self, length: int) -> str:
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    def _apply_memorability(self, password: str, config: PasswordConfig) -> str:
        if config.leetspeak:
            for char, leet in self.leetspeak_map.items():
                if random.random() > 0.5:
                    password = password.replace(char, leet)
        return password

    def _get_semantic_words(self, group: str, count: int) -> List[str]:
        if group in self.semantic_words:
            return random.sample(self.semantic_words[group], min(count, len(self.semantic_words[group])))
        return []

    def _generate_passphrase(self, config: PasswordConfig) -> str:
        if config.semantic_group:
            words = self._get_semantic_words(config.semantic_group, config.num_words)
            if len(words) < config.num_words:
                words.extend(random.sample(self.word_list, config.num_words - len(words)))
        else:
            words = random.sample(self.word_list, config.num_words)
        
        if config.capitalize_words:
            words = [word.capitalize() for word in words]
            
        if config.min_counts and config.min_counts.get('numbers'):
            numbers = ''.join(secrets.choice(string.digits) 
                            for _ in range(config.min_counts['numbers']))
            words.append(numbers)
            
        if config.min_counts and config.min_counts.get('special'):
            special = ''.join(secrets.choice(self.char_sets['special']) 
                            for _ in range(config.min_counts['special']))
            words.append(special)
            
        password = config.word_separator.join(words)
        return self._apply_memorability(password, config)

    def generate(self, config: PasswordConfig) -> str:
        self._validate_config(config)
        
        if config.type == "passcode":
            return self._generate_passcode(config.length)
            
        if config.type == "passphrase":
            return self._generate_passphrase(config)
        
        if config.complexity in self.complexity_presets:
            preset = self.complexity_presets[config.complexity]
            config.use_sets = config.use_sets or preset['use_sets']
            config.min_counts = config.min_counts or preset['min_counts']
            config.length = config.length or preset['length']
            
        chars = ''
        for set_name, use in config.use_sets.items():
            if use and set_name in self.char_sets:
                chars += self.char_sets[set_name]
                
        if config.avoid_ambiguous:
            chars = ''.join(c for c in chars if c not in self.char_sets['ambiguous'])
        if config.avoid_similar:
            chars = ''.join(c for c in chars if c not in self.char_sets['similar'])
        if config.exclude:
            chars = ''.join(c for c in chars if c not in config.exclude)
            
        if not chars:
            raise ValueError("No valid characters available after applying exclusions")
            
        password = list(config.include)
        
        if config.min_counts:
            for char_type, count in config.min_counts.items():
                valid_chars = [c for c in self.char_sets[char_type] if c in chars]
                if not valid_chars:
                    raise ValueError(f"No valid characters available for {char_type}")
                password.extend(secrets.choice(valid_chars) for _ in range(count))
                
        remaining = config.length - len(password)
        if remaining > 0:
            password.extend(secrets.choice(chars) for _ in range(remaining))
            
        if config.pattern:
            return self._apply_pattern(password, config.pattern, chars)
            
        password = self._shuffle_and_validate(password, config.consecutive_unique)
        final_password = ''.join(password)
        
        if config.memorability == "easy":
            final_password = self._apply_memorability(final_password, config)
            
        return final_password

    def _apply_pattern(self, chars: List[str], pattern: str, valid_chars: str) -> str:
        pattern_map = {
            '#': string.digits,
            '@': string.ascii_letters,
            '$': self.char_sets['special'],
            '*': valid_chars
        }
        
        result = list(pattern)
        available_chars = chars.copy()
        
        for i, pattern_char in enumerate(result):
            if pattern_char in pattern_map:
                valid = [c for c in available_chars if c in pattern_map[pattern_char]]
                if not valid:
                    raise ValueError(f"Cannot satisfy pattern at position {i}")
                chosen = secrets.choice(valid)
                result[i] = chosen
                available_chars.remove(chosen)
                
        return ''.join(result)

    def _shuffle_and_validate(self, password: List[str], consecutive_unique: bool) -> List[str]:
        if not consecutive_unique:
            random.shuffle(password)
            return password
            
        max_attempts = 100
        while max_attempts > 0:
            random.shuffle(password)
            if not any(password[i] == password[i+1] for i in range(len(password)-1)):
                return password
            max_attempts -= 1
            
        raise ValueError("Could not generate password with unique consecutive characters")

    def calculate_entropy(self, password: str) -> float:
        char_set_size = len(set(password))
        return len(password) * (char_set_size.bit_length())

    def estimate_strength(self, password: str) -> str:
        entropy = self.calculate_entropy(password)
        if entropy < 35:
            return "weak"
        elif entropy < 60:
            return "medium"
        elif entropy < 80:
            return "strong"
        return "very strong"

def get_password_config(user_input: str) -> Dict[str, Any]:
    system_prompt = """You are a password configuration analyzer. Convert user requests into a precise JSON configuration. Return ONLY a JSON object.

For numeric requirements:
- When digits/numbers are mentioned, set type to "passcode"
- Always set a positive integer for length (minimum 4)
- For digit-only passwords, disable all character sets except numbers

Required JSON format with default values:
{
    "length": 12,
    "complexity": "medium",
    "type": "password",
    "memorability": "standard",
    "use_sets": {
        "uppercase": true,
        "lowercase": true,
        "numbers": true,
        "special": true
    },
    "min_counts": {
        "uppercase": 0,
        "lowercase": 0,
        "numbers": 0,
        "special": 0
    },
    "include": "",
    "exclude": "",
    "pattern": null,
    "avoid_ambiguous": false,
    "avoid_similar": false,
    "consecutive_unique": false,
    "word_separator": "-",
    "capitalize_words": false,
    "num_words": 4,
    "leetspeak": false,
    "semantic_group": null
}

Example mappings:
1. "create easy to remember password with 8 digits" →
{
    "length": 8,
    "type": "passcode",
    "complexity": "low",
    "memorability": "easy",
    "use_sets": {"uppercase": false, "lowercase": false, "numbers": true, "special": false},
    "min_counts": {"numbers": 8},
    "consecutive_unique": true,
    "avoid_ambiguous": true
}

2. "generate secure password" →
{
    "length": 16,
    "type": "password",
    "complexity": "high",
    "memorability": "complex",
    "use_sets": {"uppercase": true, "lowercase": true, "numbers": true, "special": true},
    "min_counts": {"uppercase": 2, "lowercase": 2, "numbers": 2, "special": 2}
}

Key rules:
1. Never return null/None values for required fields
2. Always include length as positive integer
3. Always specify complete use_sets object
4. Set appropriate type based on requirements (password/passcode/passphrase)
5. Handle numeric requirements by setting type="passcode"
6. Default to secure settings when request is ambiguous"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    try:
        config = json.loads(response.choices[0].message.content)
        # Ensure critical fields have default values
        config["length"] = max(4, config.get("length", 12))
        config["type"] = config.get("type", "password")
        config["complexity"] = config.get("complexity", "medium")
        config["memorability"] = config.get("memorability", "standard")
        return config
    except json.JSONDecodeError:
        return {
            "length": 12,
            "type": "password",
            "complexity": "medium",
            "memorability": "standard",
            "use_sets": {"uppercase": True, "lowercase": True, "numbers": True, "special": True}
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        user_input = request.form.get('specification', '')
        config_dict = get_password_config(user_input)
        
        password_config = PasswordConfig(
            length=config_dict.get("length", 12),
            complexity=config_dict.get("complexity", "medium"),
            type=config_dict.get("type", "password"),
            memorability=config_dict.get("memorability", "standard"),
            use_sets=config_dict.get("use_sets"),
            min_counts=config_dict.get("min_counts"),
            include=config_dict.get("include", ""),
            exclude=config_dict.get("exclude", ""),
            pattern=config_dict.get("pattern"),
            avoid_ambiguous=config_dict.get("avoid_ambiguous", False),
            avoid_similar=config_dict.get("avoid_similar", False),
            consecutive_unique=config_dict.get("consecutive_unique", False),
            word_separator=config_dict.get("word_separator", "-"),
            capitalize_words=config_dict.get("capitalize_words", False),
            num_words=config_dict.get("num_words", 4),
            leetspeak=config_dict.get("leetspeak", False),
            semantic_group=config_dict.get("semantic_group")
        )
        
        generator = EnhancedPasswordGenerator()
        password = generator.generate(password_config)
        strength = generator.estimate_strength(password)
        
        return jsonify({
            'password': password,
            'strength': strength,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

if __name__ == '__main__':
    app.run(debug=True)
