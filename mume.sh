#!/bin/sh
export PATH=.:$PATH
[ -f .login ] || {
	echo "#NOP if you want you can put your login and password below, on two separate lines." >.login
}
pidof mmapper || {
	echo "Starting mmapper..."
	mmapper &
       	sleep 5
}
tt++ -G tintin/main.tin
