#!/bin/bash


current_branch=$(git rev-parse --abbrev-ref HEAD)


echo "Pushing $current_branch and tags to origin..."

git push origin "$current_branch"

git push origin --tags


echo "Pushing $current_branch and tags to gitlab..."

git push gitlab "$current_branch"

git push gitlab --tags


echo "Done."

