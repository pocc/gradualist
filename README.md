# Gradualism

*Gradually automate your procedures, one step at a time*

Inspired by https://blog.danslimmon.com/2019/07/15/ 

## Features

### Main Features

* Converts a markdown file into interactive steps
* Saves results into another markdown file
* On 100% automated, saves results into a script file instead

### Keywords

Start steps with these words to use them.
Using these words also makes it clearer what you want your user to do.

1. Enter: *single line answer*
    Synonyms that trigger: Type, Write, Provide,
    1. Store `{response}` in variables like so.
    2. In steps after previous, `{words}` will be replaced whatever you entered.
    3. Input is entered on a single line
    4. Automatically triggered if there is a `{variable}`
2. Describe: *longform answer*
    Synonyms that trigger: Explain
    1. Store multiline `{response}` in variables like so.
    2. In steps after previous, `{response}` will be replaced whatever you entered.
    3. Type done on a newline to signify the end of input
3. Run: *runs code*
    Synonyms that trigger: Exec, Execute
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
4. While: *Loops until condition*
    Synonyms that trigger: Loop
    * Format is 'While condition do task'
    * While condition, keep on doing it 
5. If: Conditional
    Synonym for else: Otherwise, elsewise
    Synonym for then: First comma
    * Format is 'if condition then task1 else task2'
    * Example: "if it's sunny, then have a picnic else read a book inside"
7. Click: *Have the user click somewhere*
    * This can be automated with clicking with x,y coordinates
    * Use the browser extension to select the element
8. Select
    * Select from multiple options, usually in a dropdown
    * Use the browser extension to select the element
9. Open: Open a file or URL
    * If opening a URL, default browser will be used
    * Include the words 'with program' to specify which program to open it with (i.e. firefox
      instead of chrome)
    * Include the word 'new' to create a new one if one doesn't exist
10. Transclude filepath:task list
    * Include a separate markdown procedure as a sublist of the current task
12. *Anything Else*
    * The point of this is to be as compatible with as many procedures as
      possible, so don't require keywords 
    * There won't be any suggestions for automation 

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
