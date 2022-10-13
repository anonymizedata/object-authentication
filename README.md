# General comments

On the following files, the variable _base_path_ must be changed to a local path:

* `dataset_generation.py`
* `reliable_information.py`
* `main.py`

## Python packages

**Optional:** Create a virtual environment for running the code. The list of required packages is at
the `requirements.txt` file.

```shell
pip install -r requirements.txt
```

# Image generation file

The `dataset_generation.py` file generates the images for both enrollment and authentication phases with the provided
reference images (__dataset/reference_images__).

# main.py

Variables and functions are defined for running both phases: enrollment and authentication. The code can also be run in
parallel by changing the number of cores (`N_CORES`).

By default, the algorithm runs the _case1_ and it can be changed in the variable `case = ' case2'`.  