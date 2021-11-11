### Provision user accounts

1. What is your {{name}}?
2. Run `$ ssh-keygen -t rsa -f $HOME/.ssh/{{name}}`
3. Copy ~/new_key.pub into the user_keys Git repository, then run:
    git commit {{name}}
    git push
4. Wait for the build job at http://example.com/builds/user_keys to finish
5. Go to http://example.com/directory
    Find the email address for user {{name}}
6. What is the {{email address}}?
7. Go to 1Password 

```python3
import webbrowser
webbrowser.open("https://1password.com/")
```

8. Paste the contents of ~/new_key into a new document
9. Share the document with {{email address}}
10. What is your {{personal password}}
