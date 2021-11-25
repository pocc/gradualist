# GraduaList

Automate your runbooks, one step at a time

Inspired by https://blog.danslimmon.com/2019/07/15/

*This is still being built. Expect things to break.*

## Features

### Main Features

* Converts a markdown file into interactive steps
* Saves results into another markdown file
* On 100% automated, saves results into a script file instead

### Philosophy

* Runbooks should be interactive with timestamps
* 1 runbook <=> 1 markdown file
* Directions should be in readable English

### Ancillary features

* Sublists are marked like 1.1.3 (first step, first substep, third sub-substep)
* Go back one step
* On 100% automated, saves results into a script file instead
* Saved files have tasks with
    * Timestamp of when tasks were completed
    * How long tasks took
    * Whether tasks were completed, skipped, or not done
* Transclusion syntax: Include the file in your `imports:`
    * Include another gradual list with /relative/path/to/source file, as long as that file ends with .md.
    * Then you can reference any section or step

## Todo

### Shortterm

### Longterm

* How will this interact with mdx?
* How would you reference other documents (i.e. imports)
* Migrate to rust

## Similar Ideas

There are many ideas for how to have executable runbooks.

https://docs.gitlab.com/ee/user/project/clusters/runbooks/
