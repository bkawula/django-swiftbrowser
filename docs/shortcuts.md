# Shortcuts
Here are a few Swiftbrowser related shortcuts that may make development more convenient. Add these to your ```~/.bash_profile``` file (for mac) or ```~/.bashrc``` (for Ubuntu)

Depending on how you organize your files, a quick shortcut to CD into your swiftbrowser environment will be convenient.

```bash
alias swiftbrowser="cd <asbolute-path-to-your-virtual-env>"
```

If you're using a virtual environment, this is a handy way to launch the swiftbrowser within the environment. If you're not using a virtual environemnt, you can remove the middle part.
```bash
alias runsb="swiftbrowser && source bin/active && python django-swiftbrowser/myproj/manage.py runserver"
```

Quick launch of PDB
```bash
alias pdbsb="swiftbrowser && source bin/activate && python -m pdb django-swiftbrowser/myproj/manage.py runserver --nothreading --noreload"
```

Lastly if you can't remember these shortcuts, a shortcut to list your shortcuts:

For Mac
```bash
alias shortcuts="cat ~/.bash_profile"
```

For Ubuntu
```bash
alias shortcuts="cat ~/.bashrc"
```
