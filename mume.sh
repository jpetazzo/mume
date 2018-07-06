#!/bin/sh
export PATH=.:$PATH
command -v tt++ || {
	echo "Command not found: tt++."
        echo "Suggestion: install package 'tintin++'."
	exit 1
}
command -v mmapper || {
	echo "Command not found: mmapper."
	echo "Suggestion: install it from https://github.com/MUME/MMapper"
	exit 1
}
[ -f .login ] || {
	echo "#NOP if you want you can put your login and password below, on two separate lines." >.login
}
pidof mmapper || {
	echo "Starting mmapper..."
	mmapper &
       	sleep 5
}
tt++ -G tintin/main.tin
