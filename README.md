# Gradualist

Gradually automate your procedures, one step at a time

Inspired by https://blog.danslimmon.com/2019/07/15/

## Features

### Main Features

* Converts a markdown file into interactive steps
* Saves results into another markdown file
* On 100% automated, saves results into a script file instead

### Ancillary features

* Sublists are marked like 1.1.3 (first step, first substep, third sub-substep)
* Go back one step

## Keywords

All keywords are case insensitive.

### Starting keywords

Start steps with these words to use them.
Using these words also makes it clearer what you want your user to do.

1. Enter: *store single line answer*
    Synonyms that trigger: Type, Write
    1. Store `{response}` in variables like so.
    2. In steps after previous, `{words}` will be replaced whatever you entered.
    3. Input is entered on a single line
    4. Automatically triggered if there is a `{variable}`, even if a keyword isn't present
    5. If no curly braces around a variable, everything after 'Enter' becomes the variable name
2. Describe: *longform answer*
    Synonyms that trigger: Explain
    1. Store multiline `{response}` in variables like so.
    2. In steps after previous, `{response}` will be replaced whatever you entered.
    3. If a `{variable}` isn't provided, words after Describe are the variable
    4. Type enter twice to signify the end of input
    5. Starting with a question word or including a ? will force a step to be a multiline answer
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

   ---

4. While: *Loops until condition*
    Synonyms that trigger: Loop
    * Format is 'While condition do task'
    * While condition, keep on doing it
5. For: *Loops over array*
    * Format is 'For [el1, el2, ...], do task'
    * Example: "For ["blue", "orange", "yellow"], use {} marker in your drawing
    * Generates array-length tasks
6. If: Conditional
    Synonym for else: Otherwise, elsewise
    Synonym for then: First comma
    * Format is 'if condition then task1 else task2'
    * Example: "if it's sunny, then I'll have a picnic else I'll read a book inside"
        * Variable its_sunny would get a value
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
10. Import filepath:task list
    * Include a separate markdown procedure as a sublist of the current task
11. *Anything Else*
    * The point of this is to be as compatible with as many procedures as
      possible, so don't require keywords
    * There won't be any suggestions for automation

On 100% automated, saves results into a script file instead

### Anywhere keywords

* **Personal**: Input is entered with no visible output like a password (i.e. Enter your personal password)

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
* Configuration in a yaml file

### Longterm

* How will this interact with mdx?
* How would you reference other documents (i.e. imports)
* Migrate to rust
