# Tests

## Test Keywords

1. Run `echo Hello World!`
expect: "Hello World!\n"

## Test Code Snippets

c: gcc -o temp.c; ./temp.c
cpp: g++ -o temp.cpp; ./temp.cpp
go: go run temp.go
java: javac Temp.java; java Temp
rust: rustc temp.rs; ./temp
r: r -f temp.r

No extension required: $command $file
    python, perl, php, ruby, bash, lua, julia, lisp, groovy

1. Run C

    ```c
    #include <stdio.h>
    int main() {
        printf("%s", "Hello World!\n");
    }
    ```

    expect: "Hello World!\n"

2. Run Cpp

    ```cpp
    #include <iostream>
    int main() {
        std::cout << "Hello World!" << std::endl;
    }
    ```

    expect: "Hello World!\n"

3. Run Go

    ```go
    package main
    import "fmt"
    func main() {
        fmt.Println("Hello World!")
    }
    ```

    expect: "Hello World!\n"

4. Run Java

    ```java
    public class temp {
        public static void main(String[] args) {
            System.out.println("Hello, World");
        }
    }
    ```

    expect: "Hello World!\n"

5. Run Rust

    ```rust
    fn main() {
        println!("Hello World!");
    }
    ```

    expect: "Hello World!\n"

6. Run PHP

    ```php
    <?php print "Hello World!" ?>
    ```

    expect: "Hello World!\n"

7. Run Python

    ```python
    print("Hello World!")
    ```

    expect: "Hello World!\n"

8. Run Ruby

    ```ruby
    puts "Hello World!"
    ```

    expect: "Hello World!\n"

9. Run Javascript

    ```javascript
    console.log("Hello World!")
    ```

    expect: "Hello World!\n"

10. Run Bash

    ```bash
    echo Hello World!
    ```

    expect: "Hello World!\n"

11. Run Perl

    ```perl
    print("Hello, World!\n");
    ```

    expect: "Hello World!\n"

12. Run Lua

    ```lua
    print("Hello World!")
    ```

    expect: "Hello World!\n"

13. Run Julia

    ```julia
    print("Hello World!\n")
    ```

    expect: "Hello World!\n"

14. Run GNU CLisp

    ```clisp
    (format t "Hello, World!~%")
    ```

    expect: "Hello World!\n"

15. Run groovy

    ```groovy
    print "Hello World!\n"
    ```

    expect: "Hello World!\n"
