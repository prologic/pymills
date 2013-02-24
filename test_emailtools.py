#!/usr/bin/env python


from pymills.emailtools import send_email


send_email(["prologic@shortcircuit.net.au"], "Test", "Test Message",
           files=["hello.txt"])
