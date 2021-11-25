# Gradualist Markdown

The rules stated here should make fors readable English directions.
When in doubt, follow the guidance of https://commonmark.org/.

Keywords that are capitalized must be the first word of the step after the number.
Other keywords are delimiters for helping gradualist up sentences.

first word keywords:
    - Text
        - `Enter`
        - `Type`
        - `Write`
        - `Describe`
        - `Explain`
    - Logic
        - `If`
        - `While`
    - Code
        - `Run`
        - `Exec`
        - `Execute`
    - Commands
        - `Open`

delimiter keywords:
    - `${`
    - `}`
    - `not`
    - `:`
    - `,`
    - `.`

## Variables

1. ${A variable} is `[^\n\r]+` inside of curly brackets, like javascript
2. For specifying variable type
    1. with typescript types ${it is sunny outside: bool}
    2. with your own regex {email address: '\S+@\S+.\S+'}
3. Variables can be stored in the frontmatter of the runbook
4. Variables are read and compared case-insensitive, but stored and written lowercase
5. If {a variable} is not defined in the frontmatter or in a previous step, gradualist will ask what it is
6. Future occurrences of {variable} will be replaced by the value, preserving case for latter occurrences
7. Variables are stored in the frontmatter of the outputted document

## Logic

1. `If` it is sunny`,` take a walk
    1. Starts with an `If` with a capital
    2. `,` with conditional bounded by comma
    3. "it is sunny" is treated as a variable, and Variables point 5 will apply
    4. If "it is sunny" is not defined, gradualist will ask for it with [t/f]
    5. "take a walk" can instead be a reference to another step
2. `not`: can be used with if to invert the truth value of a bool-type variable
3. `While` there are dirty dishes`,` wash a dish
    1. Starts with `While` with a capital
    2. `,` with conditional bounded by comma
    3. "wash a dish" can instead be a reference to another step
4. For: Does not exist. Manually create each new task on a new line for readability.

## Getting Input

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

## Running Code

Run, aka Exec, aka Execute

1. "Run this inline `echo shell script`"
    * Start the step with the word 'run', case insensitive
    * This will run in your shell, whichever that is for your OS.
2. "Run this multiline python script, starting the step with run."

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

## Data structures

* List: `: strawberries, apples, and bananas.`
    * Meant to sound like English
    * Requires a comma after ever non-ultimate element and an `and` before the ultimate element
    * A list should have a lookbehind for a preposition like "like", "such as", "for example", "for instance", or ":"
    * If the ultimate element has a space in it, add a period, `.`, at the end of the list
* Definition: `term is <article> definition`
    * `<article>` is one of a, an, the
    * Term is on the left-hand side of an `is <article>`
    * The definition is on the right-hand side of an `is <article>`
    * Word prior to `is` must be a noun
    * `term: definition`
    * A `definition` must not have commas, semicolons, or colons as it should be a simple statement
    * Gradualist, on seeing this definition, will save term as a variable with a predefined value

## Commands

* Open: If open is the first word of a step, then open the following file or URL with the default application
    * If the following is not a file or URL, ignore

## Built-in types

These are just regexes

* email: \S+@\S+.\S+
* phoneNumber: Something from here https://stackoverflow.com/questions/123559/

## Anywhere keywords

* **Personal**: Input is entered with no visible output like a password (e.g. Enter your personal password)
