json2dcp-notebook
=================

This Jupyter Notebook leverages RapidWright to convert a nextpnr-xilinx post-route JSON netlist
into a Vivado design checkpoint file.

## Getting Started

1. Install [RapidWright](https://www.rapidwright.io/docs/Install.html):

```
git clone https://github.com/Xilinx/RapidWright.git
cd RapidWright
./gradlew compileJava
export PATH=`pwd`/bin:$PATH
echo "export CLASSPATH=`pwd`/bin:`pwd`/jars/*" > bin/rapidwright_classpath.sh
```

2. Install `rapidwright` and `jupyter` in python3 virtual environment:

```
python3 -m venv venv
source venv/bin/activate
pip3 install rapidwright jupyter
```

3. Open `json2dcp.ipynb`:

```
cd /path/to/this/repo
jupyter-notebook ./json2dcp.ipynb
```

4. Provide path to json netlist, device part name, and dcp destination path.

5. Run the notebook in order and validate the produced dcp file in Vivado.

## License

This work is licensed under the [ISC License](./LICENSE).
