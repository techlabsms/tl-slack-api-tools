# Typeform CSV Track Cleaner
If you asked in Typeform for the track with an open question,
and now you just realized that everyone just answered differently!?
how can you nor organize all this people!?

well this tool will try its best to extract the track from that field and save it in a clean way
(ready to use with the other tools)

Dont you worry, it will also let you know when it's not sure

# Set Up
## Change Configuration
### Source csv
Your CSV Source File must have columns than contains the following:

- Name Column
- Last Name Column
- email
- track field

The name of this columns on your csv can be different, but this columns **have to be present**.

if you have for example:

| What's your name?| What's your last name?| your email  | What Track Do you want to do? | 
|:-------------:|:-------------:|:-----:|:-----:|
| Max      | Mustermann | max.mm@test.link | i want to do Web Development |
| ...    | ... | ... | UX and Data Science |

set the `config.yml` file as following:
```yaml
source:
    ...
    columns:
       - name: What's your name?
       - last name: What's your last name?
       - email: your email
       - track1: What Track Do you want to do?
```
### Output csv file
just set the path in the `config.yml`

```yaml
output:
  csv: <PathTo>\responses-out.csv
```

### Possible Calling

you can use th default list, or change the possible callings for each Track
```yaml
tracks:
  AI:
    - AI
    - Artificial Intelligence
    - A Intelligence
    - Artificial I
  WebDev:
    - webdev
    - Web Development
    - Frontend
    - Backend
    - Web
    - web dev
  UX:
    - ux
    - user experience
    - uxperience
    - user x
    - UX Design
  DataSc:
    - Data Science
    - dsc
    - Data
```

### Certanity

this configures when the App will recognize the track as part of the answer (100 is a perfect string match), `91` is recommended

```yaml
fuzzy:
  certainty ratio: 91
```

## Run The script

```bash
./clean_tracks.py
```
