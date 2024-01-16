# Relational Data Modeling
## Prerequisites
Configure a modelingcourse environment with Anaconda, an open source package management system.

1. Install miniconda on your machine following the instructions:
Linux: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
Mac: https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html
Windows: https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html

2.Clone the github repository.
```
git clone https://github.com/team-data-science/relational-data-modeling.git
cd scripts
```

3.Running this command will create a new conda environment that is provisioned with most of the libraries you need for this project.

```
conda env create -f modelingenv.yml
```

4. Verify that the modelingcourse environment was created in your environments:

```
conda info --envs
```

5. Cleanup downloaded libraries (remove tarballs, zip files, etc):

```
conda clean -tp
```

6.To activate the environment:

OS X and Linux: ```$ source activate dsa2018```
Windows:```$ source activate modelingcourse```
