#!/bin/sh
export PATH=.:$PATH
pidof mmapper || mmapper &
tt++ -G tintin/main.tin
