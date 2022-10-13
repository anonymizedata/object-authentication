# Dataset 
This folder contains the reference images for the dataset creation.



# Proverif code



# Python code
## General comments

On the following files, the variable _base_path_ must be changed to your local path:

* `dataset_generation.py`
* `reliable_information.py`
* `main.py`

## Python packages

**Optional:** Create a virtual environment for running the code. The required packages are listed in the `requirements.txt` file.

```shell
pip install -r requirements.txt
```

## Dataset generation

The `dataset_generation.py` file generates the images for both the enrollment and authentication phases with the provided reference images (__dataset/reference_images__).
To run Python scripts, you need to open a command-line window and type `python3` followed by the script's path:

```shell
python3 $YOUR_PATH/dataset_generation.py
```

## main.py

Variables and functions are defined for running both phases: enrollment and authentication. The code can be run in parallel by changing the number of cores (`N_CORES`).

By default, the algorithm runs the _case1_ and can be changed in the variable `case = ' case2'`.

```shell
python3 $YOUR_PATH/main.py
```
