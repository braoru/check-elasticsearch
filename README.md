# check-elasticsearch

#Install

##Install check

```Bash
git clone git@github.com:braoru/check-elasticsearch.git
virtualenv check-elasticsearch
cd check-elasticsearch
source bin/activate
pip install --upgrade pip
pip install -r requirement.txt

```

##Indexed docs
```Bash
python check_elasticsearch_http_indexed_docs.py -H myels -w 3000 -c 2000 -p 9200 -s http
OK: 4258 docs indexed in 5s  | '5s_indexed_doc'=4258;3000;2000;;;

```
