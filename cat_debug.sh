#!/bin/bash

while mapfile -t -n 18 ary && ((${#ary[@]})); do
    clear
    printf '%s\n' "${ary[@]}"
    sleep 0.01
done <debug
