# Track Buddy Bot

This Bot automatises the adding of the techies to the Track Channels, and the creation of the Track Buddies Groups

The Track Buddies Groups contain techies studying the same main track during the first week 

# Set-Up

## Check your csv File

Your CSV File must have columns than contains the following:

- Name Column
- Last Name Column
- email
- main track
- second track
- third track
- fourth track

The name of this columns on your csv can be different, but this columns **have to be present**.

if you have for example:

| What's your name?| What's your last name?| your email  | 1° track  | 2nd Track  | 3rd track | 4th Track | other columns |
|:-------------:|:-------------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| Max      | Mustermann | max.mm@test.link | WebDev | AI | | | ...|
| ...    | ... | ... | UX | DataSc | WebDev | | ...|

set the `config.yml` file as following:
```yaml
columns:
   - name: What's your name?
   - last name: What's your last name?
   - email: your email
   - track1: 1° track
   - track2: 2nd Track
   - track3: 3rd track
   - track4: 4th Track
```

and the track channels to the Values that you use in the Track columns:
```yaml
track channels:
   AI: G0194S0P81M
   WebDev: G019KQKRGQK
   UX: C019KQJ7NV9
   DataSc: C019KJEK79Q
```

## Create the Track Channels
Create the Slack Channels for each track and write the channel IDs in the `config.yml` file under `track channels`,
 for example:
```yaml
track channels:
   AI: G0194S0P81M
   WebDev: G019KQKRGQK
   UX: C019KQJ7NV9
   DataSc: C019KJEK79Q
```

Make sure that the Bot App is in the channels

## Create an App in the Workspace
go to https://api.slack.com/apps/ and create a new App, Add this App to your workspace.

## Required Scope
*see https://api.slack.com/scopes*

The Bot require the following **Bot Token Scopes**:

- `channels:read`
- `chat:write`
- `chat:write.customize`
- `chat:write.public`
- `groups:read`
- `groups:write`
- `im:read`
- `im:write`
- `mpim:read`
- `mpim:write`
- `users:read`
- `users:read.email`

Does not require any **User Token Scopes**

## Configure the Buddy Channels
in the `config.yml` you will find the configuration for the Track Buddy Groups:
```yaml
buddy groups:
   prefix: trackstudy-buddies
   start message: >
      this is just a test, but of you are seeing this, it means it's working!
      So Have fun!
   members max: 3
   members min: 1
```
the `prefix` will define the name of the groups, tín this example the name of a Web Development Buddy group would be built like
`#prefix`-`track`-`groupnr` so in this case it would be `#trackstudy-buddies-webdev-1`

the `start message` is the message that the bot will send after creating the buddy group.

`members max` and  `members min` will guarantee that no group is too big or too small.

## Get the token
Copy the `Bot user OAuth Token`, and pass it as the first argument this script (you can find it under api.slack.com/apps/`APPID`/oauth?) For example:

```bash
./track-buddy.py xoxb-1234567890asdfghjklqwertzuio
```

Dont worry! the Bot will show you the groups before they are created!