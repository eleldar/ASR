# ASR service

## Environment
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
apt install ffmpeg (for Windows using exe-file)
```


## Models
```
cd api
mkdir models
cd models
wget "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"
unzip vosk-model-en-us-0.22-lgraph.zip
mv vosk-model-en-us-0.22-lgraph en
```

## Using
```
python main.py
```
from browser open adress 127.0.0.1:5000/api

## Structure
```
.
├── api
│   ├── __init__.py
│   ├── models
│   │   └── en
│   │       ├── am
│   │       │   ├── final.mdl
│   │       │   └── tree
│   │       ├── conf
│   │       │   ├── mfcc.conf
│   │       │   └── model.conf
│   │       ├── graph
│   │       │   ├── disambig_tid.int
│   │       │   ├── Gr.fst
│   │       │   ├── HCLr.fst
│   │       │   ├── phones
│   │       │   │   └── word_boundary.int
│   │       │   ├── phones.txt
│   │       │   └── words.txt
│   │       ├── ivector
│   │       │   ├── final.dubm
│   │       │   ├── final.ie
│   │       │   ├── final.mat
│   │       │   ├── global_cmvn.stats
│   │       │   ├── online_cmvn.conf
│   │       │   └── splice.conf
│   │       └── README
│   ├── recognitions.py
│   ├── tempfiles
│   │   ├── src
│   │   └── tgt
│   └── tools
│       ├── handler.py
│       ├── manager.py
│       ├── postprocess.py
│       └── preprocess.py
├── main.py
├── README.md
├── report.docx
└── requirements.txt
```
