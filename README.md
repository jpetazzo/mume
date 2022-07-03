# Skaya's MUME stash

Quick start:

- install package `tintin++`
- install mmapper (from https://github.com/MUME/MMapper)
- run `./mume.sh`

Optionally, you can create a file named `.login` looking like this:

```
#NOP this line, starting with a #, should exist to make tintin++ happy.
yourlogin
yourpassword
list l
```
(The last line is optional, and will automatically list the characters in
your account after you log in.)

After creating a character, you can:

- set one bazillion useful aliases with `#textin aliases` (it will take a minute to set them all)
- perhaps change the character set back to ASCII with `change charset ascii`
- perhaps re-enable twiddleprompts with `change prompt twiddle`


## How do I quit tintin++?

```
#end
```

