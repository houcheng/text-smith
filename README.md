This is python script project Text Smith.

It can help fix transcatiion error, summarization, write note and draw ascii bullet items, etc.
The ts utility calls AI by 

It currently supports only OPENROUTERAPI.

### Usage

ts $command $action $file

#### Run command

Run command:
```
ts write all Metting-20241112.md
ts write note Metting-20241112-fix.md
ts write all *.md
ts write all meeting-1.md meeting-2.md meeting-3.md
```

#### Init command

Init command:
```
ts init
```

The output file for "all" action would be:
- Metting-20241112-fix.md
- Metting-20241112-note.md
- Metting-20241112-.md


Another usage:

ts $action --config new-config.yml Meeting.md

### Configuration file

- File name: .ts.conf.yml
- Must be in current directory, if not, should be in home directory.
- By configuration, you can define the action and correspond prompts, see below example .ts.conf.yml


```yml
fix:
    - prompts:
        - "The attached file is a transaction by AI."
        - "Fix error and modify if sentence does not make sense."
        - "Prevent changes too much"
        - "Must write in its origin language"
note:
    - source: fix
    - prompts:
        - "Write note for the attached file"
        - "Must write in its origin language"
    - cache: true
summary:
    - source: fix
    - prompts:
        - "Write a summary for the attched file in its origin language."
    - cache: true
```

## Models

- qwq: "qwen/qwq-32b-preview"
- qq: "qwen/qwen-2.5-coder-32b-instruct"
- ss: "anthropic/claude-3.5-sonnet"
- qq72: "qwen/qwen-2.5-72b-instruct"
