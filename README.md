# retrieval_model
This was a simple retrieval system for homework. Tencent and Toutiao news search engine.
Inverted index is the core and WF-IDF for rank.
# Other features
Similar search recommended， Related news recommended Commentary analysis，Commentary analysis and so on.
A Web front-end Copy from Google, because I don't like to design such things.

TIP : MySQL Server should be installed and a database names "retrieval" should be created. And Change utils/db_connecter.py add your passwd for MySQL Server.
TIP : If you wanna run this for test, run spider and invert first before start. 

# Usage:
    admin.py <mode> [-a ASYNC]
    admin.py <mode> -f|--force
    admin.py <mode>
# Options:
    -f --force          force do
    -h                  show help

# Example:
    admin.py spider -a depart
    admin.py spider -a patch
    admin.py spider -a autorun
    admin.py invert
    admin.py invert -f
    admin.py start
