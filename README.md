This is python script project Text Smith.

It can help fix transcatiion error, summarization, write note and draw ascii bullet items, etc.
The ts utility calls AI by 

It currently supports only OPENROUTERAPI.

### Usage

ts all Metting-20241112.md
ts $action  Metting-20241112.md
ts all *.md

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
- fix:
    - pompts:
        - "The attached file is a transaction by AI."
        - "Fix error and modify if sentence does not make sense."
        - "Prevent changes too much"
        - "Must write in its origin language"
- note:
    - source: fix
    - pompts:
        - "Write note for the attached file"
        - "Must write in its origin language"
    - cache: true
- summary:
    - source: fix
    - pompts:
        - "Write a summary for the attched file in its origin language."
    - cache: true
```