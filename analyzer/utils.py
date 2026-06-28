import re
import hashlib
import requests
import string
import math
import secrets


def check_password_strength(password):
    score = 0
    feedback = []
    details = {}

    # Length
    length = len(password)
    details['length'] = length
    if length >= 16:
        score += 3
        feedback.append(('success', f'Excellent length ({length} characters)'))
    elif length >= 12:
        score += 2
        feedback.append(('success', f'Good length ({length} characters)'))
    elif length >= 8:
        score += 1
        feedback.append(('warning', f'Acceptable length ({length} chars) — aim for 12+'))
    else:
        feedback.append(('danger', f'Too short ({length} chars) — minimum 8 required'))

    # Uppercase
    upper = len(re.findall(r'[A-Z]', password))
    details['uppercase'] = upper
    if upper >= 2:
        score += 2
        feedback.append(('success', f'{upper} uppercase letters found'))
    elif upper == 1:
        score += 1
        feedback.append(('warning', 'Only 1 uppercase letter — add more'))
    else:
        feedback.append(('danger', 'No uppercase letters found'))

    # Lowercase
    lower = len(re.findall(r'[a-z]', password))
    details['lowercase'] = lower
    if lower >= 2:
        score += 2
        feedback.append(('success', f'{lower} lowercase letters found'))
    elif lower == 1:
        score += 1
        feedback.append(('warning', 'Only 1 lowercase letter — add more'))
    else:
        feedback.append(('danger', 'No lowercase letters found'))

    # Digits
    digits = len(re.findall(r'\d', password))
    details['digits'] = digits
    if digits >= 2:
        score += 2
        feedback.append(('success', f'{digits} digits found'))
    elif digits == 1:
        score += 1
        feedback.append(('warning', 'Only 1 digit — add more numbers'))
    else:
        feedback.append(('danger', 'No digits found'))

    # Special characters
    specials = len(re.findall(r'[!@#$%^&*(),.?":{}|<>_\-\[\]\/\\~`+=;\'£€]', password))
    details['special'] = specials
    if specials >= 2:
        score += 3
        feedback.append(('success', f'{specials} special characters found'))
    elif specials == 1:
        score += 1
        feedback.append(('warning', 'Only 1 special character — add more'))
    else:
        feedback.append(('danger', 'No special characters (!, @, #, $ etc.)'))

    # Common patterns
    patterns = [
        r'(.)\1{2,}',
        r'(012|123|234|345|456|567|678|789|890)',
        r'(abc|bcd|cde|def|efg|fgh|ghi|hij)',
        r'(qwerty|asdf|zxcv|qazwsx)',
    ]
    if any(re.search(p, password.lower()) for p in patterns):
        score = max(0, score - 2)
        feedback.append(('danger', 'Common patterns detected (sequential/repeated chars)'))
    else:
        feedback.append(('success', 'No common patterns detected'))

    # Dictionary words
    weak_words = ['password', '123456', 'admin', 'letmein', 'welcome',
                  'monkey', 'dragon', 'master', 'qwerty', 'abc123',
                  'iloveyou', 'sunshine', 'princess', 'football', 'shadow']
    if password.lower() in weak_words:
        score = 0
        feedback.append(('danger', '⚠️ This is a very commonly used weak password!'))

    # Entropy
    charset = 0
    if re.search(r'[a-z]', password): charset += 26
    if re.search(r'[A-Z]', password): charset += 26
    if re.search(r'\d', password): charset += 10
    if re.search(r'[^a-zA-Z0-9]', password): charset += 32
    entropy = round(length * math.log2(charset), 1) if charset > 0 else 0
    details['entropy'] = entropy

    if entropy >= 70:
        feedback.append(('success', f'Very high entropy ({entropy} bits) — extremely unpredictable'))
    elif entropy >= 50:
        feedback.append(('success', f'High entropy ({entropy} bits) — good unpredictability'))
    elif entropy >= 35:
        feedback.append(('warning', f'Moderate entropy ({entropy} bits) — could be stronger'))
    else:
        feedback.append(('danger', f'Low entropy ({entropy} bits) — easy to crack'))

    # Crack time estimate
    details['crack_time'] = estimate_crack_time(entropy)

    # Strength label
    if score >= 11:
        strength, cls, bar = 'Very Strong', 'success', 100
    elif score >= 8:
        strength, cls, bar = 'Strong', 'info', 75
    elif score >= 5:
        strength, cls, bar = 'Moderate', 'warning', 50
    elif score >= 2:
        strength, cls, bar = 'Weak', 'danger', 25
    else:
        strength, cls, bar = 'Very Weak', 'danger', 10

    return {
        'score': score,
        'strength': strength,
        'strength_class': cls,
        'bar_width': bar,
        'feedback': feedback,
        'details': details,
    }


def estimate_crack_time(entropy):
    # Assuming 10 billion guesses/second (modern GPU)
    guesses = 2 ** entropy
    seconds = guesses / 10_000_000_000

    if seconds < 1:
        return 'Instantly'
    elif seconds < 60:
        return f'{int(seconds)} seconds'
    elif seconds < 3600:
        return f'{int(seconds/60)} minutes'
    elif seconds < 86400:
        return f'{int(seconds/3600)} hours'
    elif seconds < 31536000:
        return f'{int(seconds/86400)} days'
    elif seconds < 3153600000:
        return f'{int(seconds/31536000)} years'
    else:
        return 'Centuries+'


def check_breach(password):
    try:
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        r = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=5,
            headers={'Add-Padding': 'true'}
        )
        if r.status_code == 200:
            for line in r.text.splitlines():
                h, count = line.split(':')
                if h == suffix:
                    return True, int(count)
            return False, 0
    except Exception:
        return None, 0
    return None, 0


def generate_password(length=16, use_upper=True, use_digits=True, use_special=True):
    chars = string.ascii_lowercase
    required = [secrets.choice(string.ascii_lowercase)]

    if use_upper:
        chars += string.ascii_uppercase
        required.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        chars += string.digits
        required.append(secrets.choice(string.digits))
    if use_special:
        special = '!@#$%^&*()-_=+[]{}|;:,.<>?'
        chars += special
        required.append(secrets.choice(special))

    remaining = [secrets.choice(chars) for _ in range(length - len(required))]
    pwd = required + remaining
    secrets.SystemRandom().shuffle(pwd)
    return ''.join(pwd)


def mask_password(password):
    if len(password) <= 2:
        return '*' * len(password)
    return password[0] + '*' * (len(password) - 2) + password[-1]