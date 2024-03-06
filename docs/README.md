# Contributing

## Compiling and building the documentation
Clone the repository and access the subfolder dxlib/docs to get started

```bash
git clone git@github.com:delphos-quant/dxlib.git
cd docs
```

### Requirements
Install the necessary requirements in a Python 3.10 environment with:

```bash
sudo apt-get install build-essential
pip install -r requirements.txt
```

### Building
To build the documentation, simply run

```bash
make html
```

And access the generated docs under `build/html/index.html`
