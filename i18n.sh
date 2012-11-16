#!/usr/bin/env bash

py=python

$py setup.py extract_messages
$py setup.py update_catalog
$py setup.py compile_catalog
# vim:set et sts=4 ts=4 tw=80:
