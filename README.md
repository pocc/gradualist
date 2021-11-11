# Gradualism

*Gradually automate your procedures, one step at a time*

Inspired by https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/comment-page-1/#comments

## Features

### Main Features

* Converts a markdown file into an interactive todo list
* Saves results into another markdown file
* On completion, provides % automated. 

### Syntax

1. Variables
    1. Store `{words}` in variables like so.
    2. In steps after previous, `{words}` will be replaced whatever you entered.
2. Run code
    1. Run this inline `echo shell script`
        * Start the step with the word 'run', case insensitive
        * This will run in your shell, whichever that is for your OS.
    2. Run this multiline python script, starting the step with run.
        ```python -I {example.py}
        import webbrowser
        webbrowser.open("https://python.org")
        ```
        
        * Start the step with the keyord 'run', case insensitive
        * Code needs a code fence 
        * Language suggestion is required
        * `-I` is an arg to python. Include as many options as you want.
        * If an output file is specified with curly braces, it will be saved in
            the working directory; otherwise a temporary file will be used. 

### Defaults
* Saved files have tasks with 
    * Timestamp of when tasks were completed
    * How long tasks took
    * Whether tasks were completed, skipped, or not done
    
## Todo
### Shortterm
* Separate logic for input, output, and processing
* Logic
    * loops until step complete
    * if/then statements
    * Set script variables like timeout, or autofinish after a certain time

### Longterm
* How will this interact with mdx?
* How would you reference other documents (i.e. imports)
* Migrate to rust
