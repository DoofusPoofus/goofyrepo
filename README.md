# goofyrepo

password roaster. u type a password and it tells u how fast a gpu cracks it and then roasts u

```
python3 password_roaster.py
```

it uses getpass so ur password dont show on screen and it never leaves ur computer. still dont type ur real bank password into random scripts from github tho thats kinda the whole lesson

## wat it checks

- if its in a list of super common passwords (even with p@ssw0rd style tricks or 123 at the end)
- length
- uppercase digits symbols (skiped if its 16+ chars cuz long passphrases are fine)
- keyboard walks like qwer or 1234
- the same char 3 times in a row
- years like 2024

crack time is a rough guess. it assumes 10 billion guesses a second which is about one good gpu on a fast hash. real crackers are smarter so treat it as best case

## example

typed `dragon!!`:

```
rating: instant L  (a hacker gets this before u finish blinking)
time to crack on a fast gpu: instantly

roasts:
  - u picked a top 50 password. respectfully no
  - short passwords get brute forced over a lunch break
  - no capital letters. caps lock is rite there
  - not a single number. math class trauma?

how to fix it:
  - never use a password that shows up in leaks. wordlists try those first
  - go for 12 characters minimum. length matters more than anything else
  - throw in some uppercase or just make it way longer
  - add a few digits but not at the very end where everyone puts them
```

the roasts are random so u get diffrent ones each time

## tests

```
python3 -m unittest
```
