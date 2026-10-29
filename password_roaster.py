#!/usr/bin/env python3
# password roaster
# u type a password and it tells u how bad it is and roasts u for it
# it checks the length and wat kinda characters u used and if its a known common one
# then it guesses how long a fast gpu would need to brute force it
# patterns like qwer or 2024 or aaaa make it way faster cuz crackers try those first
# nothing gets saved or sent anywere its all local

import getpass
import math
import random
import re
import string
import sys

# if ur password is in here i am dissapointed in u
COMMON_PASSWORDS = {
    "123456", "123456789", "12345678", "12345", "1234567", "1234567890",
    "password", "password1", "password123", "passw0rd", "qwerty", "qwerty123",
    "qwertyuiop", "111111", "000000", "123123", "654321", "666666", "abc123",
    "iloveyou", "admin", "admin123", "welcome", "monkey", "dragon", "letmein",
    "football", "baseball", "master", "sunshine", "princess", "shadow",
    "superman", "batman", "trustno1", "hello", "freedom", "whatever",
    "starwars", "login", "secret", "michael", "charlie", "pokemon",
    "minecraft", "fortnite", "1q2w3e4r", "zaq12wsx", "asdfgh", "asdfghjkl",
}

KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]

LEETSPEAK_BACK_TO_LETTERS = str.maketrans({
    "@": "a", "4": "a", "3": "e", "1": "i", "!": "i",
    "0": "o", "$": "s", "5": "s", "7": "t",
})

GPU_GUESSES_PER_SECOND = 10_000_000_000
SECONDS_IN_A_YEAR = 31_557_600
AGE_OF_THE_UNIVERSE_IN_YEARS = 13_800_000_000

PROBLEMS = {
    "empty": {
        "roasts": ["u typed nothing. thats not a password thats a vibe"],
        "tip": "type literally anything",
    },
    "common": {
        "roasts": [
            "this one is in every hacker wordlist since like 2009",
            "u picked a top 50 password. respectfully no",
            "a script kiddie with a toaster could get this",
            "adding numbers or @ to a common word doesnt fool anyone. wordlists already do that",
        ],
        "tip": "never use a password that shows up in leaks. wordlists try those first",
    },
    "too_short": {
        "roasts": [
            "its so short i almost missed it",
            "short passwords get brute forced over a lunch break",
        ],
        "tip": "go for 12 characters minimum. length matters more than anything else",
    },
    "only_digits": {
        "roasts": ["only numbers?? this is a pin code not a password"],
        "tip": "mix in letters. 10 possible digits vs 94 possible characters is a huge diffrence",
    },
    "no_uppercase": {
        "roasts": ["no capital letters. caps lock is rite there"],
        "tip": "throw in some uppercase or just make it way longer",
    },
    "no_digits": {
        "roasts": ["not a single number. math class trauma?"],
        "tip": "add a few digits but not at the very end where everyone puts them",
    },
    "no_symbols": {
        "roasts": ["no symbols. the shift key is crying"],
        "tip": "symbols make the pool of guesses bigger. or use a long passphrase instead",
    },
    "keyboard_walk": {
        "roasts": [
            "u just slid ur finger across the keyboard huh",
            "keyboard patterns are the first thing crackers try lol",
        ],
        "tip": "avoid rows like qwer asdf or 1234. they look random but they arent",
    },
    "repeated_characters": {
        "roasts": ["holding down one key is not a strategy"],
        "tip": "repeating the same character adds length but basically zero randomness",
    },
    "has_year": {
        "roasts": ["putting a year in it doesnt make it secure it makes it a birthday"],
        "tip": "years and birthdays are super guessable. especialy if ur on social media",
    },
}

PATTERN_PROBLEMS = {"keyboard_walk", "repeated_characters", "has_year"}

RATINGS = [
    (1, "instant L", "a hacker gets this before u finish blinking"),
    (60 * 60 * 24, "trash", "gone in under a day"),
    (SECONDS_IN_A_YEAR, "mid", "it would take a while but a determined nerd gets there"),
    (SECONDS_IN_A_YEAR * 1000, "decent", "ok not bad. not great either"),
    (math.inf, "actually solid", "fine this one is good. im still judging u tho"),
]


def looks_like_a_common_password(password):
    lowercased = password.lower()
    without_trailing_junk = lowercased.rstrip(string.digits + string.punctuation)
    without_trailing_symbols = lowercased.rstrip(string.punctuation)
    versions_to_check = {
        lowercased,
        without_trailing_junk,
        without_trailing_symbols,
        lowercased.translate(LEETSPEAK_BACK_TO_LETTERS),
        without_trailing_junk.translate(LEETSPEAK_BACK_TO_LETTERS),
    }
    return any(version in COMMON_PASSWORDS for version in versions_to_check)


def find_keyboard_walk(password, shortest_walk=4):
    lowercased = password.lower()
    for keyboard_row in KEYBOARD_ROWS:
        for start in range(len(keyboard_row) - shortest_walk + 1):
            walk = keyboard_row[start:start + shortest_walk]
            if walk in lowercased or walk[::-1] in lowercased:
                return walk
    return None


def find_password_problems(password):
    if not password:
        return ["empty"]

    problems = []
    if looks_like_a_common_password(password):
        problems.append("common")
    if len(password) < 12:
        problems.append("too_short")

    if password.isdigit():
        problems.append("only_digits")
    elif len(password) < 16:
        if not any(character.isupper() for character in password):
            problems.append("no_uppercase")
        if not any(character.isdigit() for character in password):
            problems.append("no_digits")
        if not any(character in string.punctuation for character in password):
            problems.append("no_symbols")

    if find_keyboard_walk(password):
        problems.append("keyboard_walk")
    if re.search(r"(.)\1\1", password):
        problems.append("repeated_characters")
    if re.search(r"(19|20)\d\d", password):
        problems.append("has_year")

    return problems


def count_possible_characters(password):
    pool_size = 0
    if any(character in string.ascii_lowercase for character in password):
        pool_size += 26
    if any(character in string.ascii_uppercase for character in password):
        pool_size += 26
    if any(character in string.digits for character in password):
        pool_size += 10
    if any(character in string.punctuation for character in password):
        pool_size += len(string.punctuation)
    if any(not character.isascii() or character == " " for character in password):
        pool_size += 32
    return pool_size


def estimate_seconds_to_crack(password, problems):
    if not password or "common" in problems:
        return 0.0

    character_pool = count_possible_characters(password)
    log_of_average_guesses = len(password) * math.log10(character_pool) - math.log10(2)
    log_of_seconds = log_of_average_guesses - math.log10(GPU_GUESSES_PER_SECOND)

    patterns_found = PATTERN_PROBLEMS.intersection(problems)
    log_of_seconds -= 3 * len(patterns_found)

    return 10 ** min(log_of_seconds, 300)


def make_time_sound_human(seconds):
    if seconds < 1:
        return "instantly"
    if seconds > AGE_OF_THE_UNIVERSE_IN_YEARS * SECONDS_IN_A_YEAR:
        return "longer than the universe has existed lol"

    time_units = [
        ("years", SECONDS_IN_A_YEAR),
        ("days", 60 * 60 * 24),
        ("hours", 60 * 60),
        ("minutes", 60),
        ("seconds", 1),
    ]
    for unit_name, seconds_per_unit in time_units:
        if seconds >= seconds_per_unit:
            amount = seconds / seconds_per_unit
            if amount >= 1_000_000:
                return f"about {amount:.1e} {unit_name}"
            return f"about {amount:,.0f} {unit_name}"


def pick_rating(seconds):
    for upper_limit, rating_name, rating_comment in RATINGS:
        if seconds < upper_limit:
            return rating_name, rating_comment


def roast_password(password):
    problems = find_password_problems(password)
    seconds_to_crack = estimate_seconds_to_crack(password, problems)
    rating_name, rating_comment = pick_rating(seconds_to_crack)
    return {
        "problems": problems,
        "seconds_to_crack": seconds_to_crack,
        "rating": rating_name,
        "rating_comment": rating_comment,
    }


def print_the_roast(report):
    print()
    print(f"rating: {report['rating']}  ({report['rating_comment']})")
    print(f"time to crack on a fast gpu: {make_time_sound_human(report['seconds_to_crack'])}")

    if not report["problems"]:
        print("\nno problems found. who taught u this")
        return

    print("\nroasts:")
    for problem in report["problems"][:4]:
        print(f"  - {random.choice(PROBLEMS[problem]['roasts'])}")

    print("\nhow to fix it:")
    for problem in report["problems"]:
        print(f"  - {PROBLEMS[problem]['tip']}")


def main():
    try:
        password = getpass.getpass("type a password (it wont show on screen): ")
    except (KeyboardInterrupt, EOFError):
        print("\nok bye coward")
        return 1

    print_the_roast(roast_password(password))
    return 0


if __name__ == "__main__":
    sys.exit(main())
