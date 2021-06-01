# Jupyter Notebook自动加载import项

[How to Automatically Import Your Favorite Libraries into IPython or a Jupyter Notebook](https://towardsdatascience.com/how-to-automatically-import-your-favorite-libraries-into-ipython-or-a-jupyter-notebook-9c69d89aa343)

Jupyter的python内核实际为Ipython，因此需要在C:\Users\yourusrname\.ipython\profile_default\startup\中添加py启动文件实现自动加载。

文件名格式为XX-filename.py，XX前缀为纯数字，代表加载顺序。下文为该目录的README文件内容，解释了如何读取。

```
This is the IPython startup directory

.py and .ipy files in this directory will be run *prior* to any code or files specified via the exec_lines or exec_files configurables whenever you load this profile.

Files will be run in lexicographical order, so you can control the execution order of files with a prefix, e.g.::

    00-first.py
    50-middle.py
    99-last.ipy
```
